#!/usr/bin/env python3
"""
Training script for mask detection model.
Trains a MobileNetV2-based CNN on mask detection datasets.

Usage:
    python train_model.py --data-dir /path/to/dataset --epochs 20 --batch-size 32

Expected dataset structure:
    data/
    ├── MASK_ON/
    │   ├── image1.jpg
    │   └── image2.jpg
    ├── NO_MASK/
    │   ├── image1.jpg
    │   └── image2.jpg
    └── MASK_INCORRECT/
        ├── image1.jpg
        └── image2.jpg
"""

import os
import sys
import argparse
from pathlib import Path
import numpy as np
import cv2
from datetime import datetime

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau,
    TensorBoard
)


def create_model(num_classes=3, learning_rate=1e-3):
    """
    Create a MobileNetV2-based transfer learning model.
    
    Args:
        num_classes: Number of classification classes
        learning_rate: Initial learning rate
    
    Returns:
        Compiled Keras model
    """
    # Load pre-trained MobileNetV2
    base_model = keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model
    base_model.trainable = False
    
    # Build model
    model = keras.Sequential([
        keras.layers.Input(shape=(224, 224, 3)),
        keras.layers.Rescaling(1./127.5, offset=-1),
        base_model,
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01)),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(128, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01)),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    return model


def create_data_generators(train_dir, val_split=0.2):
    """
    Create ImageDataGenerator instances for training and validation.
    
    Args:
        train_dir: Path to training data directory
        val_split: Validation split ratio
    
    Returns:
        (train_generator, validation_generator)
    """
    # Training augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=val_split
    )
    
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='training'
    )
    
    validation_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )
    
    return train_generator, validation_generator


def train_model(data_dir, epochs=20, batch_size=32, output_path=None):
    """
    Train the mask detection model.
    
    Args:
        data_dir: Path to training data
        epochs: Number of training epochs
        batch_size: Batch size for training
        output_path: Path to save trained model
    """
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return False
    
    # Check for subdirectories
    required_classes = ['MASK_ON', 'NO_MASK', 'MASK_INCORRECT']
    for cls in required_classes:
        class_path = data_path / cls
        if not class_path.exists():
            print(f"❌ Missing class directory: {class_path}")
            return False
        
        num_images = len(list(class_path.glob('*.*')))
        print(f"✓ Found {num_images} images in {cls}/")
    
    # Set output path
    if output_path is None:
        output_path = 'mask_detection_model_trained.h5'
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n🚀 Creating model...")
    model = create_model()
    
    print("\n📊 Creating data generators...")
    train_gen, val_gen = create_data_generators(str(data_path))
    
    print(f"\n📈 Training model for {epochs} epochs...")
    
    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=3,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            str(output_path),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_lr=1e-7,
            verbose=1
        ),
        TensorBoard(
            log_dir='./logs',
            histogram_freq=1
        )
    ]
    
    # Train
    history = model.fit(
        train_gen,
        epochs=epochs,
        validation_data=val_gen,
        callbacks=callbacks
    )
    
    print(f"\n✅ Model training complete!")
    print(f"📁 Model saved to: {output_path}")
    
    # Print final metrics
    final_accuracy = history.history['accuracy'][-1]
    final_val_accuracy = history.history['val_accuracy'][-1]
    print(f"\n📊 Final Accuracy: {final_accuracy:.4f}")
    print(f"📊 Final Val Accuracy: {final_val_accuracy:.4f}")
    
    # Fine-tune model
    print("\n🔧 Fine-tuning model...")
    model = keras.models.load_model(str(output_path))
    
    # Unfreeze last layers of base model
    for layer in model.layers:
        if hasattr(layer, 'trainable'):
            if 'MobileNetV2' not in str(type(layer)):
                continue
            layer.trainable = True
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-5),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Fine-tune for fewer epochs
    model.fit(
        train_gen,
        epochs=5,
        validation_data=val_gen,
        callbacks=callbacks
    )
    
    print(f"\n✅ Fine-tuning complete!")
    print(f"📁 Final model saved to: {output_path}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Train mask detection model'
    )
    parser.add_argument(
        '--data-dir',
        required=True,
        help='Path to dataset directory'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=20,
        help='Number of training epochs'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size for training'
    )
    parser.add_argument(
        '--output',
        default='mask_detection_model_trained.h5',
        help='Output path for trained model'
    )
    
    args = parser.parse_args()
    
    success = train_model(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        output_path=args.output
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
