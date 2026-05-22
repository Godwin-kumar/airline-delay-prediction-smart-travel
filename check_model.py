from tensorflow.keras.models import load_model

model = load_model("models/flight_delay_model.h5")

print("MODEL INPUT SHAPE:")
print(model.input_shape)