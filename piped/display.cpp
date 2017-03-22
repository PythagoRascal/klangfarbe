// INCLUDES
#include <iostream>
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h>
#include <signal.h>
#include <time.h>
#include <math.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>

using namespace std;


// CONSTANTS
static const char *device = "/dev/spidev0.0";
static const uint32_t SPEED = 6000000;
static const uint8_t MODE = SPI_MODE_0;
static const uint8_t BITS = 8;
static const int NOF_LEDS = 30;

static unsigned char tx[NOF_LEDS * 3];
static unsigned char rx[NOF_LEDS * 3];

static struct spi_ioc_transfer parameters[1];
static int spi;


// CUSTOM TYPES
typedef struct {
	int r;
	int g;
	int b;
} RGB;


// OPEN CONNECTION TO SPI PINS
int OpenSPI() {
	spi = open(device, O_RDWR);
		if (spi < 0) {
		fprintf(stderr, "can't open device\n");
   		return 1;
   	}

	int ret = ioctl(spi, SPI_IOC_WR_MODE, &MODE);
	if(ret == -1)
	{
		close(spi);
		fprintf(stderr, "can't set mode\n");
		return 2;
	}

	ret = ioctl(spi, SPI_IOC_WR_BITS_PER_WORD, &BITS);
	if (ret == -1) {
		close(spi);
		fprintf(stderr, "can't set bits\n");
		return 3;
	}

	ret = ioctl(spi, SPI_IOC_WR_MAX_SPEED_HZ, &SPEED);
	if (ret == -1) {
		close(spi);
		fprintf(stderr, "can't set speed\n");
		return 4;
	}

	memset( &parameters, 0, sizeof(spi) );

	parameters[0].tx_buf = (unsigned long)tx;
	parameters[0].rx_buf = (unsigned long)rx;
	parameters[0].len = (NOF_LEDS * 3);
	parameters[0].delay_usecs = 0;
	parameters[0].speed_hz = SPEED;
	parameters[0].bits_per_word = BITS;
	parameters[0].cs_change = 0;

	return 0;
}
// CLOSE CONNECTION TO SPI PINS
void CloseSPI()
{
	close(spi);
}

// STRIP MANAGEMENT
void ResetStrip()
{
	memset(tx, 0, sizeof(tx));
}
void UpdateStrip()
{
	if (ioctl(spi, SPI_IOC_MESSAGE(1), &parameters) == -1)
		fprintf(stderr, "can't transfer data\n");
}


// COLOR HELPER
RGB ConvertHSLToRGB(int hue, double saturation, double lightness) {
	double chroma = (1 - fabs((2 * lightness) - 1.0)) * saturation;
	double baseline = 1.0 * (lightness - (0.5 * chroma));
	double offset = chroma * (1.0 - fabs(fmod(hue / 60.0, 2) - 1.0));

	int side = ((hue % 360) / 60);

	RGB rgb;
	if (saturation <= 0.0) {
		rgb.r = (int)(lightness * 255);
		rgb.g = (int)(lightness * 255);
		rgb.b = (int)(lightness * 255);
		return rgb;
	}

	int chromaBaseline = (int)((chroma + baseline) * 255);
	int offsetBaseline = (int)((offset + baseline) * 255);
	int colorsBaseline = (int)(baseline * 255);

	switch (side) {
		case 0:
			rgb.r = chromaBaseline;
			rgb.g = offsetBaseline;
			rgb.b = colorsBaseline;
			break;
		case 1:
			rgb.r = offsetBaseline;
			rgb.g = chromaBaseline;
			rgb.b = colorsBaseline;
			break;
		case 2:
			rgb.r = colorsBaseline;
			rgb.g = chromaBaseline;
			rgb.b = offsetBaseline;
			break;
		case 3:
			rgb.r = colorsBaseline;
			rgb.g = offsetBaseline;
			rgb.b = chromaBaseline;
			break;
		case 4:
			rgb.r = chromaBaseline;
			rgb.g = colorsBaseline;
			rgb.b = offsetBaseline;
			break;
		case 5:
			rgb.r = chromaBaseline;
			rgb.g = colorsBaseline;
			rgb.b = offsetBaseline;
			break;
	}
	return rgb;
}


// BUFFER MANAGEMENT
void RotateBuffer(int distance)
{
	memmove(&tx[distance], &tx, sizeof(tx) - distance);
	memset(&tx, 0x00, distance);
}
void PopulateRGBBuffer(char frame[]) {
	cout << "COLORS: ";
	for (int i = 0; i < NOF_LEDS; i++) {
		int hue = i * (360.0 / NOF_LEDS);
		double lightness = (int)(frame[i]) / 255.0;
		RGB rgb = ConvertHSLToRGB(hue, 1, lightness);
		cout << "[" << rgb.r << "," << rgb.g << "," << rgb.b << "],";
		tx[(i * 3)] = rgb.r;
		tx[(i * 3) + 1] = rgb.g;
		tx[(i * 3) + 2] = rgb.b;
	}
	cout << ";" << endl;
}

void StartStreaming()
{
	struct timespec in;
	struct timespec out;

	int buffersize = 30;
	char buffer [buffersize] = { 0 };

	while (1) {
		cin.read(buffer, buffersize);
		cout << "LIGHTS: ["; for (int i = 0; i < buffersize; i++) { cout << (int)buffer[i] << ", "; } cout << "]" << endl;
		PopulateRGBBuffer(buffer);
		cout << endl;
		memset(&buffer, 0, sizeof buffer);
		UpdateStrip();

		in.tv_sec = 0;
		in.tv_nsec = 100000000;
		nanosleep(&in, &out);
	}
}

void sigterm(int signum)
{
	ResetStrip();
	UpdateStrip();
	CloseSPI();
	exit(0);
}

int main(int argc, char **argv)
{
	signal(SIGTERM, sigterm);

	if( OpenSPI() != 0 )
		return 1 ;

	StartStreaming();

	return 0;
}
