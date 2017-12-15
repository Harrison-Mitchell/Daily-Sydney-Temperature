from PIL import Image, ImageDraw
STRIP_HEIGHT = 7 # currently (2017) makes a nice square image
IMAGE_WIDTH = 1095 # currently 365 * 3 i.e 1 day = 3px wide
temps = []
# rawTemps = []

# the constant first temperature in the file
lastTemp = "24.4"
# downloaded from http://www.bom.gov.au/climate/data/
with open("data.csv", "r") as data:
    # read each line exluding the CSV header
    for line in data.readlines()[1:]:
        # if temperature is missing, use yesterday's temperature
        if ",," in line:
            line = line.replace(",,", "," + lastTemp + ",")
        segment = line.split(",")
        # keep only year, month, day and temperature
        temps.append([*segment[2:5], float(segment[5])])
        # rawTemps.append(float(segment[5]))
        # make todays temperature now "yesterday's"
        lastTemp = segment[5]

# originally used the min and max for calculations but
# these extreme values then meant there was less of
# a color range for the rest of the image to use
# i.e the image was mostly orange (mid range of yellow-red)
minTemp = 10 #min(rawTemps)
maxTemp = 40 #max(rawTemps)
# if each line is 7 pixels tall, calculate final image height
height = (int(len(temps) / 365) - 2) * STRIP_HEIGHT
# create the final compilation image
overallIm = Image.new("RGB", (IMAGE_WIDTH, height), color="white")
# create the strip (single year) image
yearIm = Image.new("RGB", (364, 1), color="white")

# resize year strip and add to final compilation
def addToOverall(year):
    # yucky globals, reason being half laziness and half...
    # well... full laziness actually...
    global yearIm
    global overallIm
    # the original 365x1 image is very small
    yearIm = yearIm.resize((IMAGE_WIDTH, STRIP_HEIGHT))
    # calculate the year
    yearNum = int(year) - 1861
    # and thus how low the strip should be
    overallIm.paste(yearIm, (0, yearNum * STRIP_HEIGHT))

day = 0
lastYear = 1859
for line in temps:
    # if it's not 1859 (bad data) and it's not a leap day (uneven strip lengths)
    if line[0] != "1859" and not (line[1] == "02" and line[2] == "29"):
        # if this day is still within the same year
        if line[0] == lastYear:
            # find what color the day should be between 10-40 scaled to 0-255
            point = (line[3] - minTemp) / (maxTemp - minTemp) * 255
            # again, we didn't use absolute top and bottom, we picked numbers
            # that would create a better spread of colors, so the edge temperatures
            # would cause errors corrected here
            if point > 255: point = 255
            if point < 0: point = 0
            # place the day's pixel on the x coordinate according to day (0<=x<=364)
            # the color should be between yellow (255,255,0) and red (255,0,0)
            yearIm.putpixel((day, 0), (255, 255 - int(point), 0))
            day += 1
        # if it's the beginning of a new year
        else:
            # add last year's strip to the compilation
            addToOverall(line[0])
            # reset the strip image to white and the original size
            yearIm = Image.new("RGB", (364, 1), color="white")
            # update the comparison year
            lastYear = str(int(lastYear) + 1)
            day = 0

# the current year doesn't compare to the year in the future
# e.g if it's mid 2017, a 2018 line is never seen and the loop breaks
# so we need to add the imcomplete year to the final image
addToOverall(line[0])
overallIm.save("hot.png")