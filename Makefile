#------------------------------------------------------------------------------
# Makefile for TEPRA printer driver
# nyacom (C) 2024
#------------------------------------------------------------------------------
CUPS_HOME = /usr/lib/cups

install:
	cp cups/tepraprint-pstopng $(CUPS_HOME)/filter/
	cp cups/tepraprint $(CUPS_HOME)/backend/

uninstall:
	rm $(CUPS_HOME)/filter/tepraprint-pstopng
	rm $(CUPS_HOME)/backend/tepraprint

setup-printer:
	lpadmin -p "TEPRA-SR920" -v tepraprint:// -P cups/sr920.ppd -E

remove-printer:
	lpadmin -x "TEPRA-SR920"
