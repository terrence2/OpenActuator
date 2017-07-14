# Make sure we're not in AP mode as soon as possible.
import network
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
