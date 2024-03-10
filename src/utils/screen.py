from win32.lib import win32con
import win32api, win32gui, win32print


# 获取真实的分辨率
def getRealScreenSize():
    hDC = win32gui.GetDC(0)
    width = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    height = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return width, height


# 获取缩放后的分辨率
def getScreenSize():
    width = win32api.GetSystemMetrics(0)
    height = win32api.GetSystemMetrics(1)
    return width, height


# 获取屏幕的缩放比例
def getScreenScale():
    width1, _ = getRealScreenSize()
    width2, _ = getScreenSize()
    proportion = round(width1 / width2, 2)
    return proportion


if __name__ == '__main__':
    print("屏幕真实分辨率：", getRealScreenSize())
    print("缩放后的屏幕分辨率：", getScreenSize())
    print("屏幕缩放比：", getScreenScale())
