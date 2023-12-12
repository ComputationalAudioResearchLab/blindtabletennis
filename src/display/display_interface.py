from collections import deque
import datetime
import pathlib
import time

import event_stream
import neuromorphic_drivers as nd
import numpy as np
import vispy.app
import vispy.gloo
import vispy.util.transforms

vispy.app.use_app(backend_name="glfw")

biases = nd.prophesee_evk4.Biases(
    diff_on=120,
    diff_off=120,
)

FRAME_DURATION: float = 1.0 / 60.0
ON_COLORMAP: list[str] = ["#F4C20D", "#191919"]
OFF_COLORMAP: list[str] = ["#1E88E5", "#191919"]

VERTEX_SHADER: str = """
uniform mat4 u_projection;
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;
void main (void) {
    v_texcoord = a_texcoord;
    gl_Position = u_projection * vec4(a_position, 0.0, 1.0);
}
"""


def color_to_vec4(color: str) -> str:
    return f"vec4({int(color[1:3], 16) / 255.0}, {int(color[3:5], 16) / 255.0}, {int(color[5:7], 16) / 255.0}, 1.0)"


FRAGMENT_SHADER: str = f"""
uniform sampler2D u_texture;
uniform float u_t;
uniform float u_tau;
const float on_color_table_scale = {len(ON_COLORMAP) - 1};
const vec4 on_color_table[2] = vec4[]({','.join(color_to_vec4(color) for color in ON_COLORMAP)});
const float off_color_table_scale = {len(OFF_COLORMAP) - 1};
const vec4 off_color_table[2] = vec4[]({','.join(color_to_vec4(color) for color in OFF_COLORMAP)});
varying vec2 v_texcoord;
void main() {{
    float t_and_on = texture2D(u_texture, v_texcoord).r;
    float lambda = 1.0f - exp(-float(u_t - abs(t_and_on)) / u_tau);
    float scaled_lambda = lambda * (t_and_on > 0.0 ? on_color_table_scale : off_color_table_scale);
    gl_FragColor = t_and_on == 0.0 ? on_color_table[int(on_color_table_scale)] : mix(
        (t_and_on > 0.0 ? on_color_table : off_color_table)[int(scaled_lambda)],
        (t_and_on > 0.0 ? on_color_table : off_color_table)[int(scaled_lambda) + 1],
        scaled_lambda - float(int(scaled_lambda))
    );
}}
"""

PRIMARY_SERIAL = "00050423"
SECONDARY_SERIAL = "00050870"

class Canvas(vispy.app.Canvas):
    def __init__(
        self,
        sensor_width: int,
        sensor_height: int,
        device_primary_events: deque,
        device_secondary_events: deque,
    ):
        self.program = None
        vispy.app.Canvas.__init__(
            self,
            keys="interactive",
            size=(sensor_width / 2, sensor_height),
            vsync=True,
            title="Blind Ping pong Event Cameras",
        )
        self.sensor_width = sensor_width
        self.sensor_height = sensor_height
        self.event_streams = (device_primary_events, device_secondary_events)

        dirname = pathlib.Path(__file__).resolve().parent
        name = (
            datetime.datetime.now(tz=datetime.timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
            .replace(":", "-")
        )
        
        self.current_ts = np.array([0.0, 0.0], dtype=np.float32)
        
        self.program = vispy.gloo.Program(VERTEX_SHADER, FRAGMENT_SHADER)
        self.ts_and_ons = np.zeros(
            (self.sensor_width, 2 * self.sensor_height),
            dtype=np.float32,
        )
        self.current_t = 0
        self.offset_t = 0
        self.texture = vispy.gloo.texture.Texture2D(
            data=self.ts_and_ons,
            format="luminance",
            internalformat="r32f",
        )
        self.projection = vispy.util.transforms.ortho(
            0, sensor_width, 0, 2 * sensor_height, -1, 1
        )
        self.program["u_projection"] = self.projection
        self.program["u_texture"] = self.texture
        self.program["u_t"] = 0
        self.program["u_tau"] = 200000
        self.coordinates = np.zeros(
            4,
            dtype=[("a_position", np.float32, 2), ("a_texcoord", np.float32, 2)],
        )
        self.coordinates["a_position"] = np.array(
            [
                [0, 0],
                [sensor_width, 0],
                [0, 2 * sensor_height],
                [sensor_width, 2 * sensor_height],
            ]
        )
        self.coordinates["a_texcoord"] = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        self.program.bind(vispy.gloo.VertexBuffer(self.coordinates))
        self.projection = vispy.util.transforms.ortho(
            0,
            self.sensor_width,
            0,
            2 * self.sensor_height,
            -1,
            1,
        )
        vispy.gloo.set_clear_color("#292929")
        self.timer = vispy.app.Timer(FRAME_DURATION, connect=self.update, start=True)  # type: ignore
        self.show()

    def on_resize(self, event):
        if self.program is not None:
            width, height = event.physical_size
            vispy.gloo.set_viewport(0, 0, width, height)
            self.projection = vispy.util.transforms.ortho(
                0, width, 0, height, -100, 100
            )
            self.program["u_projection"] = self.projection
            ratio = width / float(height)
            sensor_ratio = self.sensor_width / float(2.0 * self.sensor_height)
            if ratio < sensor_ratio:
                w, h = width, width / sensor_ratio
                x, y = 0, int((height - h) / 2)
            else:
                w, h = height * sensor_ratio, height
                x, y = int((width - w) / 2), 0
            self.coordinates["a_position"] = np.array(
                [[x, y], [x + w, y], [x, y + h], [x + w, y + h]]
            )
            self.program.bind(vispy.gloo.VertexBuffer(self.coordinates))
    def draw_frame(self, index):
        if len(self.event_streams[index]) == 0:
            return
        
        #Retrieve all waiting packets
        chunks = []
        while self.event_streams[index]:
            chunks.append(self.event_streams[index].popleft())
        
        packet = np.concatenate(chunks, axis = 0)
        
        assert packet is not None
        # For online

        if "dvs_events" in packet:
            self.current_ts[index] = packet["dvs_events"]["t"][-1]
            self.program["u_t"] = self.current_ts.max()
            self.ts_and_ons[
                packet["dvs_events"]["x"],
                packet["dvs_events"]["y"] + self.sensor_height * index,
            ] = packet["dvs_events"]["t"].astype(np.float32) * (
                packet["dvs_events"]["on"].astype(np.float32) * 2.0 - 1.0
            )

        #For offline as file does not have the "dvs_events" outer dictionary

        # self.current_ts[index] = packet["t"][-1]
        # self.program["u_t"] = self.current_ts.max()
        # self.ts_and_ons[
        #     packet["x"],
        #     packet["y"] + self.sensor_height * index,
        # ] = packet["t"].astype(np.float32) * (
        #     packet["on"].astype(np.float32) * 2.0 - 1.0
        # )


    def on_draw(self, event):
        assert self.program is not None
        
        vispy.gloo.clear(color=True, depth=True)
        
        #Update both camera
        self.draw_frame(0)
        self.draw_frame(1)

        self.texture.set_data(self.ts_and_ons)
        self.program.draw("triangle_strip")