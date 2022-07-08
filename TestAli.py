# import threading, time

# x = 1
# def a():
#     threading.Timer(5, a).start()
#     global x
#     x += 1
#     print('a', x)

# def b():
#     threading.Timer(3, b).start()
#     global x
#     x += 2
#     print('b', x)

# a()
# b()

# import threading
# import time
  
# def print_cube(num):
#     """
#     function to print cube of given num
#     """
#     print("Cube: {}".format(num * num * num))
#     time.sleep(3)
#     print('End1')
  
# def print_square(num):
#     """
#     function to print square of given num
#     """
#     print("Square: {}".format(num * num))
#     time.sleep(6)
#     print('End2')
  
  
# if __name__ == "__main__":
#     # creating thread
#     t1 = threading.Thread(target=print_square, args=(10,))
#     t2 = threading.Thread(target=print_cube, args=(10,))
  
#     # starting thread 1
#     t1.start()
#     # starting thread 2
#     t2.start()
  
#     print('Running')
#     # wait until thread 1 is completely executed
#     t1.join()
#     print('t1 joined')
#     # wait until thread 2 is completely executed
#     t2.join()
#     print('t2 joined')
  
#     # both threads completely executed
#     print("Done!")
from matplotlib import pyplot as plt
import requests, json, time
