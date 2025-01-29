# ups-monitoring

Monitor UPS Lite v1.2 battery module on Raspberry Pi

### How to:
1. Clone repo;
1. Enter in repo folder: `cd ups-monitoring`
1. Create a virtual environment and install the required packages: `make deps-pi`;
1. Create a `systemd` file to auto-start the script on boot:

    ```
    # login as superuser
    sudo su

    # create file
    touch /etc/systemd/system/ups-monitoring.service

    cat << EOF > /etc/systemd/system/ups-monitoring.service
    [Unit]
    Description=UPS Monitoring
    After=network.target
    
    [Service]
    Restart=on-failure
    User=pi
    WorkingDirectory=/home/pi/ups-monitoring
    ExecStart=/home/pi/ups-monitoring/.venv/bin/python3 ups_hat.py
    
    [Install]
    WantedBy=multi-user.target
    EOF
    ```

1. Enable and start service:

    ```
    systemctl enable ups-monitoring.service &&\
      systemctl start ups-monitoring.service &&\
      systemctl status ups-monitoring.service
    ```

1. Script will run every 2 minutes, check logs inside `/home/pi/ups-monitoring/ups.log file`
