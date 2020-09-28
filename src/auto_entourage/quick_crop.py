"""
Quikly Crops Bitmap to Content.

Starting from the edges, crops a bitmap images to its first non-blank pixel.
"""
__author__ = "Vincent Mai"
__version__ = "0.1.0"

from PIL import Image
import numpy as np
import traceback
import sys
import os

def batch_crop_png(in_dir, out_dir):
    for file_name in os.listdir(in_dir):
        if file_name.endswith(".png"):
            in_path = f"{in_dir}/{file_name}"
            out_path = f"{out_dir}/trimmed_{file_name}"
            try:
                quick_crop_png(in_path, out_path)
            except:
                traceback.print_exc()
                print(file_name)
                
def quick_crop_png(in_path, out_path):
    """crops png from in_path and save to out_path
    """
    data = np.asarray(Image.open(in_path)).copy()
    alpha = data[:, :, -1]
    arr_x = np.sum(alpha, axis=0)
    arr_y = np.sum(alpha, axis=1)
    x0, x1 = find_edge(arr_x), find_edge(arr_x, reverse=True)
    y0, y1 = find_edge(arr_y), find_edge(arr_y, reverse=True)
    data = data[y0:y1, x0:x1]
    img = Image.fromarray(data)
    img.save(out_path, format='PNG')

def generate_arr(size):
    edge = np.random.randint(0, size)
    arr = np.zeros(size)
    fill = np.random.randint(low=1, high=255, size=(size-edge,))
    arr[arr.size-fill.size :] = fill
    return arr, edge

def test_generate_arr():
    for i in range(0, 100):
        arr, edge = generate_arr(np.random.randint(1, 200))
        if arr.size == 1:
            assert(edge == 0)
        elif edge == 0:
            assert(np.all(arr>0))
        else:
            assert(arr[edge] > 0 and arr[edge-1]==0)

def find_edge(arr, reverse=False):
    """Returns the first non-zero index
    """
    left, right = 0, arr.size-1
    while right > left:
        if reverse:
            mid = right - (right-left) // 2
            if arr[mid] != 0:
                left = mid
            else:
                right = mid-1
        else:
            mid = left + (right-left) // 2
            if arr[mid] != 0:
                right = mid
            else:
                left = mid+1
    return left if reverse else right

def test_find_edge():
    for i in range(0, 100):
        arr, edge = generate_arr(np.random.randint(1, 2000))
        rev_arr, rev_edge = np.flip(arr), arr.size -1 - edge
        result = find_edge(arr)
        rev_result = find_edge(rev_arr, reverse=True)
        assert(result == edge)
        assert(rev_result == rev_edge)
        
def main():
    in_dir, out_dir = sys.argv[1], sys.argv[2]
    batch_crop_png(in_dir, out_dir)

if __name__ == "__main__":
    main()