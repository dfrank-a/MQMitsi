import os
import paho.mqtt.client as mqtt

env = os.environ


class MQTTClient(mqtt.Client):
    def __init__(self):
        super().__init__(protocol=getattr(mqtt, env.get("MQTT_PROTOCOL", "MQTTv311")))

        ca_certs = env.get("CA_ROOT_CERT_FILE")

        if ca_certs is not None:
            self.tls_set(
                ca_certs,
                certfile=env.get("LOCAL_CERTIFICATE_FILE"),
                keyfile=env.get("LOCAL_PRIVATE_KEY"),
            )

        username = env.get("MQTT_USERNAME")
        if username is not None:
            password = env.get("MQTT_PASSWORD")
            self.username_pw_set(username, password=password)

    def connect(
        self,
        host=env["MQTT_BROKER_URL"],
        port=int(env.get("MQTT_BROKER_PORT", 1883)),
        *args,
        **kwargs
    ):
        return super().connect(host, port, *args, **kwargs)

    def connect_async(
            self,
            host=env["MQTT_BROKER_URL"],
            port=int(env.get("MQTT_BROKER_PORT", 1883)),
            *args,
            **kwargs
    ):
        return super().connect_async(host, port, *args, **kwargs)
