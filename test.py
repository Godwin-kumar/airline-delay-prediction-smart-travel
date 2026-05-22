from engine import init_flights, update_flights, get_positions
import threading
import time

init_flights()

threading.Thread(target=update_flights, daemon=True).start()

while True:
    data = get_positions()
    print(data[:3])  # print first 3 flights
    time.sleep(2)