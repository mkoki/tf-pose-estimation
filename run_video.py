import argparse
import logging
import time

import cv2
import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

logger = logging.getLogger('TfPoseEstimator-Video')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation Video')
    parser.add_argument('--video', type=str, default='')
#     parser.add_argument('--resolutigon', type=str, default='432x368', help='network input resolution. default=432x368')
    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    parser.add_argument('--showBG', type=bool, default=True, help='False to show skeleton only.')
    args = parser.parse_args()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w = 480
    h = 900

    e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
    cap = cv2.VideoCapture(args.video)
    img_outdir = './img３'
    os.makedirs(img_outdir, exist_ok=True)

    # 動画作成
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video  = cv2.VideoWriter('output_line_output.mp4', 10, speed, (w, h))
    
    outimg_files = []
    count = 0


    if cap.isOpened() is False:
        print("Error opening video stream or file")
    while cap.isOpened():
        ret_val, image = cap.read()

        humans = e.inference(image)
            human_pts_list = np.zeros((len(humans),18,2))
            image_h, image_w = image.shape[:2]
            for hid,human in enumerate(humans):
              for i in range(common.CocoPart.Background.value):
                if i not in human.body_parts.keys():
                  center = -1,-1
                body_part = human.body_parts[i]
                center = (int(body_part.x * image_w + 0.5), int(body_part.y * image_h + 0.5))
                human_pts_list[hid,i,0] = center[0]
                human_pts_list[hid,i,1] = center[1]
            print(human_pts_list)
            
        if not args.showBG:
            image = np.zeros(image.shape)
        image = e.draw_humans(image, humans, imgcopy=False)
        image = e.draw_humans(img, humans, imgcopy=False)

        # 画像出力
        outimg_file = '{}/{:05d}.jpg'.format(img_outdir, count)
        cv2.imwrite(outimg_file, image)
        video.write(image) 

#         cv2.putText(image, "FPS: %f" % (1.0 / (time.time() - fps_time)), (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
logger.debug('finished+')
