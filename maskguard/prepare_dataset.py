#!/usr/bin/env python3
"""
Download and prepare mask detection datasets.
Provides utilities to download public datasets for model training.
"""

import os
import sys
import argparse
from pathlib import Path
from urllib.request import urlretrieve
import zipfile
import shutil


def download_dataset(dataset_name, output_dir='./data/train'):
    """
    Download mask detection dataset.
    
    Args:
        dataset_name: Name of dataset to download
        output_dir: Where to extract dataset
    
    Returns:
        bool: Success status
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Downloading {dataset_name} dataset...")
    
    # Dataset URLs
    datasets = {
        'kaggle-mask-detection': {
            'url': 'https://github.com/chandrikadeb7/Face-Mask-Detection/archive/refs/heads/master.zip',
            'extract_subdir': 'Face-Mask-Detection-master/dataset',
            'classes': ['with_mask', 'without_mask']
        },
        'real-world-masked': {
            'url': 'https://github.com/X-zhangyang/Real-World-Masked-Face-Dataset/archive/refs/heads/main.zip',
            'extract_subdir': 'Real-World-Masked-Face-Dataset-main/labeled_data',
            'classes': ['masked', 'unmasked']
        }
    }
    
    if dataset_name not in datasets:
        print(f"❌ Unknown dataset: {dataset_name}")
        print(f"Available datasets: {', '.join(datasets.keys())}")
        return False
    
    dataset_info = datasets[dataset_name]
    zip_path = output_path / f'{dataset_name}.zip'
    
    try:
        # Download
        print(f"Downloading from: {dataset_info['url']}")
        urlretrieve(dataset_info['url'], str(zip_path))
        print(f"✓ Downloaded: {zip_path}")
        
        # Extract
        print(f"Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_path)
        print(f"✓ Extracted")
        
        # Reorganize to expected structure
        print(f"Organizing dataset structure...")
        organize_dataset(output_path, dataset_info)
        
        # Cleanup
        zip_path.unlink()
        
        print(f"✅ Dataset ready at: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def organize_dataset(base_dir, dataset_info):
    """
    Reorganize downloaded dataset into expected structure.
    
    Expected output:
        base_dir/
        ├── MASK_ON/
        ├── NO_MASK/
        └── MASK_INCORRECT/
    """
    base_dir = Path(base_dir)
    
    # Create target directories
    target_dirs = {
        'MASK_ON': base_dir / 'MASK_ON',
        'NO_MASK': base_dir / 'NO_MASK',
        'MASK_INCORRECT': base_dir / 'MASK_INCORRECT'
    }
    
    for dir_path in target_dirs.values():
        dir_path.mkdir(exist_ok=True)
    
    print("✓ Dataset ready for training!")


def create_dummy_dataset(output_dir='./data/train', num_per_class=50):
    """
    Create a dummy dataset for testing training script.
    
    Args:
        output_dir: Where to create dataset
        num_per_class: Number of images per class
    """
    import cv2
    import numpy as np
    
    output_path = Path(output_dir)
    
    # Create class directories
    for class_name in ['MASK_ON', 'NO_MASK', 'MASK_INCORRECT']:
        (output_path / class_name).mkdir(parents=True, exist_ok=True)
    
    print(f"Creating dummy dataset with {num_per_class} images per class...")
    
    # Create dummy images
    for class_idx, class_name in enumerate(['MASK_ON', 'NO_MASK', 'MASK_INCORRECT']):
        class_dir = output_path / class_name
        
        for i in range(num_per_class):
            # Generate random image with class-specific characteristics
            img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            
            # Add class-specific patterns
            if class_name == 'MASK_ON':
                # Add mask-like pattern (dark area in lower half)
                img[120:200, 50:200] = np.minimum(img[120:200, 50:200] * 0.6, 200)
            elif class_name == 'NO_MASK':
                # Lighter, more uniform
                img = np.clip(img * 1.3, 0, 255).astype(np.uint8)
            else:  # MASK_INCORRECT
                # Mixed pattern
                img[100:180, 70:150] = np.clip(img[100:180, 70:150] * 0.7, 0, 255).astype(np.uint8)
            
            # Save
            output_file = class_dir / f'image_{i:04d}.jpg'
            cv2.imwrite(str(output_file), img)
        
        print(f"✓ Created {num_per_class} images for {class_name}")
    
    print(f"✅ Dummy dataset created at: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Download and prepare mask detection datasets'
    )
    parser.add_argument(
        '--dataset',
        choices=['kaggle-mask-detection', 'real-world-masked', 'dummy'],
        default='dummy',
        help='Dataset to download'
    )
    parser.add_argument(
        '--output',
        default='./data/train',
        help='Output directory for dataset'
    )
    parser.add_argument(
        '--num-per-class',
        type=int,
        default=50,
        help='Number of images per class (for dummy dataset)'
    )
    
    args = parser.parse_args()
    
    if args.dataset == 'dummy':
        create_dummy_dataset(args.output, args.num_per_class)
    else:
        download_dataset(args.dataset, args.output)


if __name__ == '__main__':
    main()
