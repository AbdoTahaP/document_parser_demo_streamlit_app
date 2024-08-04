from typing import Tuple
import os
import numpy as np
import cv2
from paddleocr import PaddleOCR

from config import get_ocr

def __extract_text(img):
    ocr = get_ocr()
    result = ocr.ocr(img, cls=False)
    return result[0]


def __detect_checkboxes(page: np.ndarray, min_scale = 22e-5, max_scale = 50e-5, min_density = 0.05):
    def __detect_box(image,line_min_width=15):
        gray_scale=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        _, img_bin = cv2.threshold(gray_scale,150,225,cv2.THRESH_BINARY)
        kernal6h = np.ones((1,line_min_width), np.uint8)
        kernal6v = np.ones((line_min_width,1), np.uint8)
        img_bin_h = cv2.morphologyEx(~img_bin, cv2.MORPH_OPEN, kernal6h)
        img_bin_v = cv2.morphologyEx(~img_bin, cv2.MORPH_OPEN, kernal6v)
        img_bin_final = img_bin_h|img_bin_v
        final_kernel = np.ones((3,3), np.uint8)
        img_bin_final = cv2.dilate(img_bin_final,final_kernel,iterations=1)
        ret, labels, stats, centroids = cv2.connectedComponentsWithStats(~img_bin_final, connectivity=8, ltype=cv2.CV_32S)
        return stats
    
    def __is_checked(image, min_density: float = 0.05):
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image

        # Choose a threshold value for binarization
        _, binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)  # Adjust threshold if needed

        # Count non-white pixels (assuming white is 255)
        non_white_pixels = np.sum(binary_image != 255)

        # Calculate density (ratio of non-white pixels to total pixels)
        density = non_white_pixels / np.prod(binary_image.shape)

        return density > min_density
    
    stats = __detect_box(page)
    
    height = page.shape[0]
    width = page.shape[1]
    total_area = height*width
    
    boxes = []
    for x, y, w, h, area in stats:
        if area/total_area > min_scale and area/total_area < max_scale:
            is_checked_box = __is_checked(page[y:y+h, x:x+w], min_density)
            if is_checked_box:
                color = (0, 255, 0)
                box = [[x, y], [x+w, y], [x+w, y+h], [x, y+h]] # [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
                text = ("(checked)", 0.7)
                out = [box, text]
            else:
                color = (0, 0, 255)
                box = [[x, y], [x+w, y], [x+w, y+h], [x, y+h]] # [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
                text = ("(unchecked)", 0.7)
                out = [box, text]
            boxes.append(out)
            cv2.rectangle(page, (x, y), (x+w, y+h), color, 10)
            
    return boxes


def get_raw_text_from_pages(page, filename: str, page_num: int = 1, save_images: bool = False):
    checkboxes = __detect_checkboxes(page)
    result: list = __extract_text(page)
    if checkboxes:
        result.extend(checkboxes)
        result = sorted(result, key= lambda x: x[0][0][1])
    if save_images:
        out_folder='out'
        os.makedirs(out_folder, exist_ok=True)
        cv2.imwrite(f"{out_folder}/{filename.split('/')[-1].split('.')[0] if '/' in filename else filename.split('.')[0]}_page_{page_num}.png", page)
    raw_text = "\n".join([line[1][0] for line in result])
    return result, raw_text


def __intersection(box_1, box_2):
    return [box_2[0], box_1[1], box_2[2], box_1[3]]


def __iou(box_1, box_2):
    x_1 = max(box_1[0], box_2[0])
    y_1 = max(box_1[1], box_2[1])
    x_2 = min(box_1[2], box_2[2])
    y_2 = min(box_1[3], box_2[3])

    inter = abs(max((x_2 - x_1, 0)) * max((y_2 - y_1), 0))
    if inter == 0:
        return 0

    box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
    box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))

    return inter / float(box_1_area + box_2_area - inter)

def __nms(bboxes,psocres,threshold):
    #Unstacking Bounding Box Coordinates
    bboxes = bboxes.astype('float')
    x_min = bboxes[:,0]
    y_min = bboxes[:,1]
    x_max = bboxes[:,2]
    y_max = bboxes[:,3]
    
    #Sorting the pscores in descending order and keeping respective indices.
    sorted_idx = psocres.argsort()[::-1]
    #Calculating areas of all bboxes.Adding 1 to the side values to avoid zero area bboxes.
    bbox_areas = (x_max-x_min+1)*(y_max-y_min+1)
    
    #list to keep filtered bboxes.
    filtered = []
    selected_indices = []
    while len(sorted_idx) > 0:
        #Keeping highest pscore bbox as reference.
        rbbox_i = sorted_idx[0]
        #Appending the reference bbox index to filtered list.
        filtered.append(rbbox_i)
        selected_indices.append(rbbox_i)
        
        #Calculating (xmin,ymin,xmax,ymax) coordinates of all bboxes w.r.t to reference bbox
        overlap_xmins = np.maximum(x_min[rbbox_i],x_min[sorted_idx[1:]])
        overlap_ymins = np.maximum(y_min[rbbox_i],y_min[sorted_idx[1:]])
        overlap_xmaxs = np.minimum(x_max[rbbox_i],x_max[sorted_idx[1:]])
        overlap_ymaxs = np.minimum(y_max[rbbox_i],y_max[sorted_idx[1:]])
        
        #Calculating overlap bbox widths,heights and there by areas.
        overlap_widths = np.maximum(0,(overlap_xmaxs-overlap_xmins+1))
        overlap_heights = np.maximum(0,(overlap_ymaxs-overlap_ymins+1))
        overlap_areas = overlap_widths*overlap_heights
        
        #Calculating IOUs for all bboxes except reference bbox
        ious = overlap_areas/(bbox_areas[rbbox_i]+bbox_areas[sorted_idx[1:]]-overlap_areas)
        
        #select indices for which IOU is greather than threshold
        delete_idx = np.where(ious > threshold)[0]+1
        delete_idx = np.concatenate(([0],delete_idx))
        
        #delete the above indices
        sorted_idx = np.delete(sorted_idx,delete_idx)
        
    
    #Return filtered bboxes
    return selected_indices

def __get_data(img, output):
    image_height = img.shape[0]
    image_width = img.shape[1]

    boxes = np.array([line[0] for line in output])
    texts = np.array([line[1][0] for line in output])
    probabilities = np.array([line[1][1] for line in output])

    horiz_boxes = []
    vert_boxes = []

    for box in boxes:
        x_h, x_v = 0, int(box[0][0])
        y_h, y_v = int(box[0][1]), 0
        width_h, width_v = image_width, int(box[2][0] - box[0][0])
        height_h, height_v = int(box[2][1] - box[0][1]), image_height

        horiz_boxes.append(np.array([x_h, y_h, x_h + width_h, y_h + height_h]))
        vert_boxes.append(np.array([x_v, y_v, x_v + width_v, y_v + height_v]))
        
    horiz_boxes = np.array(horiz_boxes)
    vert_boxes = np.array(vert_boxes)
    
    horiz_out = __nms(horiz_boxes, probabilities, 0.5)
    horiz_lines = np.sort(horiz_out)
    
    vert_out = __nms(vert_boxes, probabilities, 0.5)
    vert_lines = np.sort(vert_out)

    out_array = [[] for _ in range(len(horiz_lines))]

    unordered_boxes = []

    for i in vert_out:
        unordered_boxes.append(vert_boxes[i][0])

    ordered_boxes = np.argsort(unordered_boxes)
    added = set()
    for i in range(len(horiz_lines)):
        for j in range(len(vert_lines)):
            resultant = __intersection(
                horiz_boxes[horiz_lines[i]], vert_boxes[vert_lines[ordered_boxes[j]]]
            )

            for b in range(len(boxes)):
                the_box = [
                    boxes[b][0][0],
                    boxes[b][0][1],
                    boxes[b][2][0],
                    boxes[b][2][1],
                ]
                hashable_box = tuple(the_box)
                if __iou(resultant, the_box) > 0.2:
                    if hashable_box in added:
                        continue
                    out_array[i].append([b, the_box])
                    added.add(hashable_box)
    # out_text = []
    # for items in out_array:
    #     items = sorted(items, key = lambda x: x[1][0])
    #     items = out_text.append(" ".join(texts[item[0]] for item in items))
    
    # out_text = np.array(out_text)
    # return out_text
    
    space_ratio = 0.04561003420752566
    space_size = image_width * space_ratio
    
    tab_ratio = 0.18244013683010263
    tab_size = image_width * tab_ratio

    out_text = []
    num_of_tabs = int(image_width/tab_size)
    tab_indent = [tab_size*i for i in range(1,num_of_tabs+1)]
    for items in out_array:
        items = sorted(items, key = lambda x: x[1][0])
        text = ""
        for j in range(len(items)):
            if j < len(items) - 1:
                curr, nxt = items[j], items[j+1]
                curr_end = items[j][1][2]
                nxt_start = items[j+1][1][0]
                tab_value = 0
                for idx, val in enumerate(tab_indent):
                    if val > nxt_start:
                        tab_value = tab_indent[idx-1]
                # tab_value = next((val for x, val in enumerate(tab_indent) if val <= nxt_start), None)
                num_spaces = int((tab_value - curr_end)/space_size) + int((nxt_start - tab_value)/space_size) if tab_value != 0 else 1
                text += f" {texts[items[j][0]] + (' '*num_spaces)}"
            else:
                text += f" {texts[items[j][0]]}"
        # items = out_text.append(" ".join(texts[item[0]] for item in items))
        out_text.append(text.strip())
    
    out_text = np.array(out_text)
    return out_text


def get_processed_text_from_pages(img, result):
    output = __get_data(img, result)
    processed_text = "\n".join(text for text in output).replace("    ", "\t").strip()
    return processed_text


