import numpy as np
from typing import List, Tuple, Dict
from collections import OrderedDict

class CentroidTracker:
    """
    Simple centroid-based object tracker.
    
    Assigns IDs to objects based on nearest centroid distance.
    """
    
    def __init__(self, max_disappeared: int = 30):
        """
        Initialize the centroid tracker.
        
        Args:
            max_disappeared: Maximum frames an object can disappear before being removed
        """
        self.next_object_id = 0
        self.objects: OrderedDict[int, Tuple[float, float]] = OrderedDict()
        self.disappeared: Dict[int, int] = {}
        self.max_disappeared = max_disappeared
    
    def register(self, centroid: Tuple[float, float]) -> int:
        """
        Register a new object with the next available ID.
        
        Args:
            centroid: (x, y) coordinates of object center
        
        Returns:
            The assigned object ID
        """
        object_id = self.next_object_id
        self.objects[object_id] = centroid
        self.disappeared[object_id] = 0
        self.next_object_id += 1
        return object_id
    
    def deregister(self, object_id: int):
        """
        Deregister an object ID.
        
        Args:
            object_id: ID to remove
        """
        del self.objects[object_id]
        del self.disappeared[object_id]
    
    def update(self, boxes: List[Tuple[int, int, int, int]]) -> List[Tuple[int, Tuple[int, int, int, int]]]:
        """
        Update the tracker with new detections.
        
        Args:
            boxes: List of bounding boxes as (x1, y1, x2, y2)
        
        Returns:
            List of (object_id, box) tuples
        """
        # If no detections, mark all as disappeared
        if len(boxes) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                
                # Deregister if disappeared too long
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            
            return []
        
        # Compute centroids for new boxes
        input_centroids = []
        for box in boxes:
            x1, y1, x2, y2 = box
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            input_centroids.append((cx, cy))
        
        # If no existing objects, register all as new
        if len(self.objects) == 0:
            results = []
            for i, box in enumerate(boxes):
                object_id = self.register(input_centroids[i])
                results.append((object_id, box))
            return results
        
        # Get existing object IDs and centroids
        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())
        
        # Compute distance matrix between existing and new centroids
        distances = np.zeros((len(object_centroids), len(input_centroids)))
        
        for i, obj_centroid in enumerate(object_centroids):
            for j, input_centroid in enumerate(input_centroids):
                dx = obj_centroid[0] - input_centroid[0]
                dy = obj_centroid[1] - input_centroid[1]
                distances[i, j] = np.sqrt(dx * dx + dy * dy)
        
        # Match objects to new centroids using nearest neighbor
        # Sort by distance and match greedily
        rows = distances.min(axis=1).argsort()
        cols = distances.argmin(axis=1)[rows]
        
        used_rows = set()
        used_cols = set()
        
        results = []
        
        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue
            
            # Match found
            object_id = object_ids[row]
            self.objects[object_id] = input_centroids[col]
            self.disappeared[object_id] = 0
            
            used_rows.add(row)
            used_cols.add(col)
            
            results.append((object_id, boxes[col]))
        
        # Handle unmatched existing objects (disappeared)
        unused_rows = set(range(distances.shape[0])) - used_rows
        for row in unused_rows:
            object_id = object_ids[row]
            self.disappeared[object_id] += 1
            
            if self.disappeared[object_id] > self.max_disappeared:
                self.deregister(object_id)
        
        # Handle unmatched new detections (register as new)
        unused_cols = set(range(distances.shape[1])) - used_cols
        for col in unused_cols:
            object_id = self.register(input_centroids[col])
            results.append((object_id, boxes[col]))
        
        return results

# Global tracker instance
centroid_tracker = CentroidTracker(max_disappeared=30)
