# ups-monitoring

Monitor UPS battery module with Raspberry Pi

### How to:
1. Install create a virtual environment: `make venv`;
1. Install required packages: `make install`;
1. Create a crontab entry to auto start script on boot:

    ```
    # open crontab for current user
    crontab -e

    # add the line bellow at the end of file
    @reboot /home/pi/ups/.venv/bin/python3 /home/pi/ups/ups_hat.py
    ```
1. Script will run on every 2 minutes, check logs inside `/home/pi/ups/ups.log file`
