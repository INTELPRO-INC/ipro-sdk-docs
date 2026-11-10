---
title: "Image Teach in the Browser"
description: Image Teach for the IPRO7AI Reef EVK in Chrome or Edge with the SDK's tools/teach_web - start the local server, record, train in the browser, deploy over Web Serial, use it offline, and how it differs from IPRO AI Studio.
---

# Image Teach in the Browser

The SDK's `tools/teach_web` is image Teach without installing IPRO AI Studio: open a local web page in Chrome or Edge, record in front of the Reef's camera, train in the browser, and deploy to the board over the same USB-C cable with Web Serial. The flow is that of Studio's **Teach** page, and the model it builds is identical to Studio's, byte for byte. It works on Windows, macOS and Linux.

## Prerequisites { #prerequisites }

- An IPRO7AI Reef EVK with the OV5640 camera (SW7 at CAM), flashed with the Edge AI firmware and in `image` mode. The page cannot switch modes: if the board is in another mode, type `mode image` on the console or use Studio's **Switch to Teach** first. See [Flash the Edge AI Firmware](firmware.md#modes).
- A USB-C data cable from the Reef's USB-C to the computer: it powers the board and carries both the video and the model.
- Chrome or Edge (they have Web Serial; Safari and Firefox do not).
- Python 3.8 or later, only to serve the page on this computer.
- SDK V2.2.1: `tools/teach_web/`.

## Start the page { #start }

<div class="ipro-steps" markdown>

1. **Start the local server** from the SDK root:

    ```bash
    python3 tools/teach_web/serve.py
    ```

    It serves `tools/teach_web/` to this computer only (127.0.0.1) at `http://localhost:8780` and opens it in the default browser. If that is not Chrome or Edge, paste the address into one. The camera and serial port are only available to pages from `localhost` or `https`; opening `index.html` from disk does not work.

2. **Allow the camera**: the first time, the browser asks to use the camera; allow it.

3. **Pick the Reef's camera**: choose **IPRO7 UVC Cam** in the **Camera** menu. The bright square is what the model sees.

</div>

`serve.py` options: `--port <port>` for another port, `--no-browser` to not open a browser, and `--fetch-runtime` (see [Use it offline](#offline)).

## Collect, train, deploy { #steps }

<div class="ipro-steps" markdown>

1. **Collect**: select a class, put the object in the square, and hold **Hold to record** (or the space bar) for a few seconds. Keep the **BACKGROUND** class, recorded with nothing in the square, so the board can say "nothing there". Up to 8 classes; names use A-Z and 0-9, up to 15 characters, because the board draws them in its own font. Press **Review** to look through the pictures, tick bad ones and press **Delete selected**, then **Done**.

2. **Train**: choose a backbone (MobileNetV2 0.35 or MobileNetV1 0.25) and press **Train**; it takes a second or two. One picture in every four of each class is held out and scored; pictures from one recording look alike, so read the score as "the classes are separable", not as accuracy on new scenes.

3. **Connect the board**: press **Connect…** (or the first **Deploy**); the browser asks which serial port to use - pick **IPRO7 UVC Cam**.

4. **Deploy**: press **Deploy**. The page runs **Build the model**, **Send and write** and **Restart the board**: it builds the model and sends it with the labels, and the board checks and writes it and restarts; the camera comes back by itself. A refused or interrupted transfer never touches the model already on the board.

5. **Run it on the board**: the board classifies the square on its own NPU and draws the label, its confidence and every class's probability beside the square.

</div>

**Save…** and **Open…** keep a set of pictures in a `.teach` file, to add to it or train it again later.

## Verify { #verify }

1. After the deploy the camera view comes back, with the class name and probabilities beside the square.
2. Each class's object in the square shows that class; an empty square shows **BACKGROUND**.
3. The same view shows in Studio or in any program that can open a USB camera.

## Use it offline { #offline }

The page runs its backbone with LiteRT.js and downloads it from the jsDelivr CDN unless a local copy exists. Before using a computer without internet, run this once on a computer with internet (about 22 MB, checked against the npm integrity hash):

```bash
python3 tools/teach_web/serve.py --fetch-runtime
```

The runtime is stored in `tools/teach_web/vendor/`; copy that folder along to the offline computer.

## Voice page { #voice-page }

`voice.html` (the **Voice** tab at the top of the page) is voiceprint recognition in the browser. With the Reef in `voice` mode, press **Connect…** and pick **IPRO Reef Voice**; you can then enroll speakers (**Teach a voice**, **Record**), press **Start listening** to see who is speaking, and use **Stranger mode** and **Thresholds**. Everything runs on the board; the page only sends commands and draws the labels it gets back. The controls mean the same as on Studio's Audio page; see [Voiceprint Recognition](voice.md).

## Compared with IPRO AI Studio { #compare }

| | Browser, `tools/teach_web` | IPRO AI Studio |
|---|---|---|
| Where to get it | Ships with the SDK | [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) |
| What to install | Python 3.8 or later and Chrome or Edge | The Studio application |
| Operating systems | Windows, macOS, Linux | macOS, Windows |
| Image recognition | Yes: collect, train, deploy | Yes (**Teach** page) |
| Voiceprint recognition | Yes (`voice.html`) | Yes (**Audio** page) |
| Sensor recognition | No | Yes (**Sensor** page) |
| Switching the board's mode | No; use the console's `mode` or Studio | **Switch to …** button |
| Keeping collected pictures | A `.teach` file | A folder (one sub-folder of PNG files per class) |
| Command line, `.ipkg` model packages | No | The `ipro-ai` command line |
| Internet | Needed once to download LiteRT.js, or fetched beforehand with `--fetch-runtime` | Not needed |

Both build the same image model byte for byte: the classification layer trained in the browser is written straight into the bundled template `.inm`, with no model converter.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| `This browser has no Web Serial` | The browser lacks Web Serial | Use Chrome or Edge |
| `Open this page from http://localhost` | The page was opened from disk | Start it with `serve.py` and open `http://localhost:8780` |
| No **IPRO7 UVC Cam** in the camera list | The board is not in `image` mode, does not run the Edge AI firmware, or the cable is charge-only | Type `mode image` on the console; use a data cable |
| `The camera went away` after a deploy | The board is restarting | Normal; the camera comes back by itself. If not, unplug and replug USB-C |
| On macOS no program shows the camera | Another program still holds the camera | Quit it, then unplug and replug USB-C |
| `The model runtime did not load` | No internet and no local copy | Run `serve.py --fetch-runtime` on a computer with internet, or copy `vendor/` over |

## Next steps { #next-steps }

- [Image Recognition](image.md): Studio's Teach page, with command-line training and model packages.
- [Sensor Recognition](sensor.md): available in Studio only.
