from PIL import Image
import sys
import os
import random


class CustomImage:
    def __init__(self, color_value=(0, 0, 0), width=255, height=255, file_name="default_file_name"):
        self.color_value = color_value
        self.file_name = file_name
        self.img = Image.new('RGB', (width, height), (color_value[0], color_value[1], color_value[2]))

    def save(self):
        self.img.save(self.file_name + ".png", "PNG")
        pass

    def show(self):
        self.img.show()


class JunkImages:
    def __init__(self):
        pass

    @staticmethod
    def add_junk_images_to_dir(dir_arg, percentage_arg=None):
        original_directory = os.getcwd()
        os.chdir(dir_arg)

        # get image count
        img_count = len([name for name in os.listdir('.') if name[-4:] == ".png"])

        # select % of random images and produce similar junk based on color
        percent = .2                                            # default
        if percentage_arg:
            percent = float(percentage_arg)
        n_a = [name for name in os.listdir('.') if name[-4:] == ".png"]  # all image names
        random.shuffle(n_a)
        a = n_a[:int(percent * len(n_a))]

        for full_img_name in a:
            im = Image.open(full_img_name)

            new_image_name = full_img_name[:-5] + chr(ord(full_img_name[-5]) + 1)    # creates a believable image name

            rgb_im = im.convert('RGB')
            r, g, b = rgb_im.getpixel((1, 1))

            c = CustomImage((r, g, b), im.size[0], im.size[1], new_image_name)
            c.save()
        os.chdir(original_directory)

    @staticmethod
    def retrieve_names_of_junk_files(dir_arg):
        original_directory = os.getcwd()
        os.chdir(dir_arg)
        junk_files = []
        n_a = [name for name in os.listdir('.') if name[-4:] == ".png"]  # all image names

        for file_name in n_a:
            desired_file_name = file_name[:-5] + chr(ord(file_name[-5]) + 1) + '.png'
            if desired_file_name in n_a:
                junk_files.append(desired_file_name)
        os.chdir(original_directory)
        return junk_files

if __name__ == "__main__":
    # being run directly / not imported
    print "\nTo add junk images to a directory, identify a directory with pngs and:"
    print "\n\tpython custom_junk_images.py c <directory_name> <optional_percentage>"
    print "\n\tpython custom_junk_images.py c gen/gen .2"
    print "\n\nTo retrieve junk images in a directory, select a directory with pngs and:"
    print "\n\tpython custom_junk_images.py r <directory_name>\n\n"

    ji = JunkImages()
    command_arg = sys.argv[1]
    dir_arg = sys.argv[2]
    if command_arg == 'c':
        percentage_arg = '.2'   # sys.argv[3]
        if len(sys.argv) == 4:
            percentage_arg = sys.argv[3]
        ji.add_junk_images_to_dir(dir_arg, percentage_arg)
    elif command_arg == 'r':
        print ji.retrieve_names_of_junk_files(dir_arg)

