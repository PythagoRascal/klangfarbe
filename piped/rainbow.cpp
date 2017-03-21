#include <iostream>
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h>
#include <signal.h>
#include <time.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>

static const char *device = "/dev/spidev0.0";
static const uint32_t SPEED = 6000000;
static const uint8_t MODE = SPI_MODE_0;
static const uint8_t BITS = 8;

static const int NOF_LEDS = 30;

static unsigned char tx[NOF_LEDS * 3];
static unsigned char rx[NOF_LEDS * 3];

static struct spi_ioc_transfer parameters[1];

static int spi;

using namespace std;

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

void CloseSPI()
{
	close(spi);
}

void ResetStrip()
{
	memset(tx, 0, sizeof(tx));
}

void UpdateStrip()
{
	if (ioctl(spi, SPI_IOC_MESSAGE(1), &parameters) == -1)
		fprintf(stderr, "can't transfer data\n");
}

void PushBuffer(int distance)
{
	memmove(&tx[distance], &tx, sizeof(tx) - distance);
	memset(&tx, 0x00, distance);
}

void ShowRainbow()
{
	struct timespec in;
	struct timespec out;

	int i = 0;
	int cols [12] = { 0xFF0000, 0xFFF000, 0xFFFF00, 0xF0FF00, 0x00FF00, 0x00FFF0, 0x00FFFF, 0x00F0FF, 0x0000FF, 0xF000FF, 0xFF00FF, 0xFF00F0 };
	while (1) {
		PushBuffer(3);

		int  col = cols[i];
		tx[0] = (col >> 16) & 0xFF;
		tx[1] = (col >> 8) & 0xFF;
		tx[2] = col & 0xFF;

		i = ++i % 12;
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

	ShowRainbow();

	return 0;
}
