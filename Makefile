PORT ?= DONT_FORGET_TO_SET_PORT
BAUD ?= 115200
MODEL ?= NONE
AMPY ?= ./.venv/bin/ampy

install_OpenActuator:
	$(AMPY) -p $(PORT) -b $(BAUD) put OpenActuator/boot.py
	$(AMPY) -p $(PORT) -b $(BAUD) put OpenActuator/main.py
	$(AMPY) -p $(PORT) -b $(BAUD) put OpenActuator/app_a/

install_config:
	$(AMPY) -p $(PORT) -b $(BAUD) mkdir config
	$(AMPY) -p $(PORT) -b $(BAUD) put examples/diagnostic_led-$(MODEL).pin config/diagnostic_led.pin
	$(AMPY) -p $(PORT) -b $(BAUD) put config.json config/config.json
	$(AMPY) -p $(PORT) -b $(BAUD) put auth.json config/auth.json
