# ups-monitoring

Monitor UPS battery module with Raspberry Pi

### How to:
1. Clone repo;
1. Install create a virtual environment: `make deps-pi`;
1. Create a crontab entry to auto start script on boot:

    ```
    # open crontab for current user
    crontab -e

    # add the line bellow at the end of file
    @reboot /home/pi/ups-raspberrypi/.venv/bin/python3 /home/pi/ups-raspberrypi/ups_hat.py
    ```
1. Script will run on every 2 minutes, check logs inside `/home/pi/ups-raspberrypi/ups.log file`
