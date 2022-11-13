import datetime
import os
import random
import time


def thread_function(name):
    # volume 1%, XXX=0.01 and YYY=-4000 (10^(-4000/2000)=10^-2=0.01
    # volume 10%, XXX=0.1 and YYY=-2000 (10^(-2000/2000)=10^-1=0.1
    # volume 50%, XXX=0.5 and YYY=-602 (10^(-602/2000))~=0.5
    # volume 100%, XXX=1 and YYY=0 (10^(0/2000)=10^0=1)
    # volume 150%, XXX=1.5 and YYY=352 ... (for boost test, normal values are <=100%)
    #os.system('/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/ogg/hello.ogg')

    # Setting up a random integer to pick 1 of 13 soundbytes
    choice = random.randint(1, 13)
    #cur_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #cur_time = str(datetime.now().strftime('%H:%M:%S'))
    cur_time = datetime.datetime.now()

    # Only way that works is to write to a file and read it's timestamp
    path = r"log.txt"
    # file creation timestamp in float
    c_time = os.path.getctime(path)
    # convert creation timestamp into DateTime object
    dt_c = datetime.datetime.fromtimestamp(c_time)
    print('Logfile Created on:', dt_c)

    time.sleep(1)

    file1 = open("log_new.txt", "w")
    file1.write(str(cur_time))
    file1.close()

    # Create a new file, compare its timestamp to a file created when previous file was played
    path_new = r"log_new.txt"
    # file modification timestamp of a file
    #m_time = os.path.getmtime(path_new)
    m_time = os.path.getctime(path_new)
    # convert timestamp into DateTime object
    dt_m = datetime.datetime.fromtimestamp(m_time)
    print('Logfile Modified on:', dt_m)

    # check the time difference between the timestamps
    delta = dt_m - dt_c
    difference = delta.total_seconds()
    print('Time gap between soundbytes: ', difference)

    if (choice == 1 and difference >= 20):
        # write to the file, we'll check the file again when another face is detected
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system(
            '/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/ogg/hello.ogg')
    elif (choice == 2 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system(
            '/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/you-stupid-whats-910.mp3')
    elif (choice == 3 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system('/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/wrong-the-only-checking-out-you-will-do-will-be-to-check-out-of-here.mp3')
    elif (choice == 4 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system(
            '/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/why-is-6-afraid-of-7.mp3')
    elif (choice == 5 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system(
            '/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/what-did-0-say-to-8.mp3')
    elif (choice == 6 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system('/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/theres-one-in-every-family-sire-two-in-mine-actually-and-they-always-manage-to-ruin-special-occasions.mp3')
    elif (choice == 7 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system(
            '/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/new-siri-0-divided-by-0.mp3')
    elif (choice == 8 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system('/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/its-mr-banana-beak-to-you-fuzzy-and-right-now-we-are-all-in-very-real-danger.mp3')
    elif (choice == 9 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system('/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/im-an-exceptional-thief-mrs-mcclain-and-since-im-moving-up-to-kidnapping-you-should-be-more-polite.mp3')
    elif (choice == 10 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system('/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/hes-as-mad-as-a-hippo-with-a-hernia.mp3')
    elif (choice == 11 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system('/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/hed-make-a-very-handsome-throw-rug-zazu-and-just-think-whenever-he-gets-dirty-you-could-take-him-out-and-beat-him.mp3')
    elif (choice == 12 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system('/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/didnt-your-mother-ever-tell-you-not-to-play-with-your-food.mp3')
    elif (choice == 13 and difference >= 20):
        file1 = open("log.txt", "w")
        file1.write(str(cur_time))
        file1.close()
        os.system('/usr/bin/omxplayer --vol -2000 /home/pi/Downloads/OpenCV/face_detection/sound/mp3/and-with-an-attitude-like-that-im-afraid-youre-shaping-up-to-be-a-pretty-pathetic-king-indeed.mp3')
