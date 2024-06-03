import os
from tkinter import Tk, Canvas, filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import math
import requests
import json
import pyautogui
import sys



class ImageApp():
    def __init__(self, root):
        self.root = root
        self.canvas = Canvas(root)
        self.canvas.pack()

        self.num_lines = simpledialog.askinteger("Input", "Enter the number of lines to draw:", minvalue=1)
        if self.num_lines is None:
            messagebox.showinfo("Info", "No number entered, exiting.")
            sys.exit()

        self.select_image()
        # self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-1>", self.mouse_click)
        self.canvas.bind("<B1-Motion>", self.mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_release)

        self.click_x = None
        self.click_y = None
        self.temp_line = None
        self.temp_line_arrow = []
        self.lines = []  # To store the coordinates of lines
        self.points = []  # To store click coordinates and angles
        self.lines_drawn = 0  # To count the number of lines drawn
        self.disable_click = False  # To disable clicking on image after reaching the specified number of lines

    def resize_image(self, image_path):
        # Screen size
        screen_width, screen_height = pyautogui.size()
        print("screen_size:", screen_width, screen_height)
        img = Image.open(image_path)
        # resized_img = img.resize((1088, 912))
        # 保存缩放后的图片
        # resized_img.save("resized_image.jpg")
        width, height = img.size
        # # 转换原点为左下角
        # img = img.transpose(Image.FLIP_TOP_BOTTOM)
        if width > screen_width*2/3 or height > screen_height:
            new_width = width // 2
            new_height = height // 2
            print("缩放后的尺寸：", new_width, new_height)
            resized_img = img.resize((new_width, new_height))
        else:
            resized_img = img
        img.close()
        return resized_img

    def select_image(self):
        image_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if image_path:
            resized_img = self.resize_image(image_path)
            # 保存缩放后的图片
            resized_img.save("resized_image.jpg")
            resizeed_img_path = "resized_image.jpg"
            self.original_image = self.show_image(resizeed_img_path)
        else:
            messagebox.showinfo("Info", "No image selected, exiting.")
            sys.exit()

    def show_image(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.config(width=self.image.width, height=self.image.height)
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        self.root.title(f"Viewing {os.path.basename(image_path)}")

    def mouse_click(self, event):
        self.click_x, self.click_y = event.x, event.y
        print(f"Mouse pressed at ({self.click_x}, {self.click_y}) in image {self.image_path}")

    def mouse_move(self, event):
        if self.temp_line:
            self.canvas.delete(self.temp_line)
        self.temp_line = self.canvas.create_line(self.click_x, self.click_y, event.x, event.y, fill="red", width=2)
        if self.temp_line_arrow:
            for line in self.temp_line_arrow:
                self.canvas.delete(line)
        self.temp_line_arrow = self.draw_temporary_arrow(event.x, event.y)

    # 未使用，因为导航到指定坐标，需要传入的是gridposition和angle
    # 将栅格化坐标（像素坐标）转换为世界坐标，根据公式：word = grid * reslution + oringin(由地图信息得到)
    def point_change(self, point, mapinfo):
        originX, originY, resolution = mapinfo
        word_x = point[0] * resolution + originX
        word_y = point[1] * resolution + originY
        word_point = [word_x, word_y]
        return word_point

    def mouse_release(self, event):
        release_x, release_y = event.x, event.y
        print(f"Mouse released at ({release_x}, {release_y}) in image {self.image_path}")
        self.lines.append(((self.click_x, self.click_y), (release_x, release_y)))
        angle = self.calculate_angle(self.click_x, self.click_y, release_x, release_y)

        # 图片路径
        image_path = "resized_image.jpg"
        # 打开图片文件
        img = Image.open(image_path)
        # 获取图片的宽度和高度
        width, height = img.size
        # # 打印图片的宽度和高度
        # print("图片宽度:", width)
        # print("图片高度:", height)
        # 关闭图片文件
        img.close()

        point = [self.click_x, self.click_y, angle]
        # 获取RGB中某点是以左上角为像素原点的，而栅格化坐标是以右下角为原点的，需做转换，再验证
        point = [point[0], height-point[1], point[2]]

        self.points.append(point)
        print(f"Recorded line info: {point}")  # Print the most recently added line info
        print(f"All recorded points: {self.points}")  # Print all points
        if self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None
        if self.temp_line_arrow:
            for line in self.temp_line_arrow:
                self.canvas.delete(line)
            self.temp_line_arrow = []
        self.draw_lines()
        self.lines_drawn += 1
        if self.lines_drawn >= self.num_lines:
            print("Reached the number of lines to draw.")
            self.disable_click = True  # Disable clicking on image
            # self.canvas.unbind("<Button-1>")

        if len(self.points) >= self.num_lines:
            print("Reached the number of lines to draw.")
            self.disable_click = True
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            # sys.exit()
            # self.root.quit() # Close the Tkinter window and exit the main loop

    def calculate_angle(self, x1, y1, x2, y2):
        image_height = self.image.height
        dx = x2 - x1
        dy = (image_height - y2) - (image_height - y1)  # Converting y to coordinate system with origin at bottom-left
        angle = math.degrees(math.atan2(dy, dx))
        return angle

    def draw_arrow(self, draw, x1, y1, x2, y2, arrow_length=10, arrow_angle=30):
        # Draw the line
        draw.line((x1, y1, x2, y2), fill="red", width=2)

        # Calculate the angle of the line
        angle = math.atan2(y2 - y1, x2 - x1)

        # Calculate the points of the arrowhead
        angle1 = angle + math.radians(arrow_angle)
        angle2 = angle - math.radians(arrow_angle)
        x1_arrow = x2 - arrow_length * math.cos(angle1)
        y1_arrow = y2 - arrow_length * math.sin(angle1)
        x2_arrow = x2 - arrow_length * math.cos(angle2)
        y2_arrow = y2 - arrow_length * math.sin(angle2)

        # Draw the arrowhead
        draw.line((x2, y2, x1_arrow, y1_arrow), fill="red", width=2)
        draw.line((x2, y2, x2_arrow, y2_arrow), fill="red", width=2)

    def draw_temporary_arrow(self, x2, y2, arrow_length=10, arrow_angle=30):
        lines = []
        # Calculate the angle of the line
        angle = math.atan2(y2 - self.click_y, x2 - self.click_x)

        # Calculate the points of the arrowhead
        angle1 = angle + math.radians(arrow_angle)
        angle2 = angle - math.radians(arrow_angle)
        x1_arrow = x2 - arrow_length * math.cos(angle1)
        y1_arrow = y2 - arrow_length * math.sin(angle1)
        x2_arrow = x2 - arrow_length * math.cos(angle2)
        y2_arrow = y2 - arrow_length * math.sin(angle2)

        # Draw the arrowhead
        lines.append(self.canvas.create_line(x2, y2, x1_arrow, y1_arrow, fill="red", width=2))
        lines.append(self.canvas.create_line(x2, y2, x2_arrow, y2_arrow, fill="red", width=2))

        return lines

    def draw_lines(self):
        # Redraw the original image
        self.image = Image.open(self.image_path)
        draw = ImageDraw.Draw(self.image)
        for line in self.lines:
            self.draw_arrow(draw, *line[0], *line[1])
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        # Draw the lines on the canvas
        for line in self.lines:
            self.canvas.create_line(line[0], line[1], fill="red", width=2)
            self.draw_temporary_arrow(*line[1])

    # def ctl_car(self):
    #     # 小车IP地址
    #     IP_URL = 'http://10.7.5.88:8080'
    #     url = '/gs-robot/cmd/navigate'
    #     # 询问用户是否执行控制小车的代码块
    #     confirm = messagebox.askyesno("Confirmation", "Do you want to control the robot?")
    #
    #     # 如果用户点击了确认按钮，则执行控制小车的代码块
    #     if confirm:
    #         # try:
    #         # 循环遍历points中的每个坐标点
    #         for point in self.points:  # 测试这个self.points的数据是否正常
    #             x, y, angle = point[0]*2, point[1]*2, point[2]
    #             # 构造POST请求的参数
    #             params = {  # ori1
    #                 "destination": {
    #                     "angle": angle,
    #                     "gridPosition": {
    #                         "x": x,
    #                         "y": y
    #                     }
    #                 }
    #             }
    #
    #             # 发送POST请求到小车IP地址
    #             response = requests.post(IP_URL + url, json.dumps(params))
    #
    #             # 打印响应内容和状态码
    #             print("Response:", response.text)
    #             print("Status Code:", response.status_code)
    #
    #             # 检查响应状态码，根据需要进行处理
    #             if response.status_code == 200:
    #                 print("Successfully sent command to the robot.")
    #             else:
    #                 print("Failed to send command to the robot.")
    #                 messagebox.showerror("Error", "Failed to connect to the robot.\nPlease check and try it again.")
    #                 self.root.quit()
    #     else:
    #         print("Operation canceled by the user.")

if __name__ == "__main__":
    root = Tk()
    app = ImageApp(root)
    root.mainloop()
