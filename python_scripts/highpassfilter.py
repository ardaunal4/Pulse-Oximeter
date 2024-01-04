import numpy as np
import matplotlib.pyplot as plt

alpha = 0.99999

def hpf(array):

    output = [i for i in array]

    for counter in range(len(array)-1):
        output[counter+1] = alpha*output[counter] + array[counter + 1] - array[counter]

    return output

def main():

    y = []
    x = []

    t = np.arange(0, 10, 1e-3)

    sin_func = 2 + 2*np.sin(2*np.pi*t)
    filtered_sin_func = hpf(sin_func)

    print("Average of Original Signal = ", np.average(sin_func))
    print("Average of Filtered Signal = ", np.average(filtered_sin_func))

    plt.figure(figsize = (10, 8))
    plt.plot(t, sin_func, "b-", label = "Original Signal")
    plt.plot(t, filtered_sin_func, "r-", label = "Filtered Signal")
    plt.xlabel("time")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid("on")
    plt.show()

if __name__ == "__main__":
    main()
