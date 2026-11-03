---
title: "Image Recognition"
description: Teach the IPRO7AI Reef EVK your own objects on IPRO AI Studio's Teach page - switch to image mode, check the camera, create classes, record, train, deploy, watch the result on the board, then add samples and retrain.
---

# Image Recognition

Hold your objects in front of the Reef's camera for a few seconds each, train on the computer and deploy to the board. From then on the board's NPU classifies whatever is in the box at the center of the camera view and draws the answer on the camera stream. It all happens on IPRO AI Studio's **Teach** page, with no code.

## Prerequisites { #prerequisites }

- An IPRO7AI Reef EVK flashed with the Edge AI firmware; see [Flash the Edge AI Firmware](firmware.md).
- The OV5640 camera module: plug its cable into FPC1 with the board unpowered, and set SW7 to CAM. Always unplug USB-C before plugging or unplugging the camera cable.
- A USB-C data cable from the Reef's USB-C to the computer.
- IPRO AI Studio installed and allowed to use the camera; see [Install IPRO AI Studio](install.md).

## How it works { #how-it-works }

- The OV5640 captures 1280×720 and the ISP makes two outputs at once: a 640×360 preview, compressed to MJPEG and sent to the computer as a standard USB camera (UVC), and the box at the center, scaled to 128×128 for the NPU.
- The box at the center of the preview is exactly what the model sees. The Teach page cuts the same box out of the preview as training pictures ("crops").
- The model is a frozen MobileNet backbone plus a classification layer. Only the last layer is trained, so training takes seconds on the computer's CPU. Every layer runs on the NPU.
- On a deploy, Studio sends the model and the class names over the USB serial port. The board checks the size, CRC-32 and model format, writes the model to flash only if they are right, and restarts by itself.
- The board draws its result outside the box. The inside of the box always stays the camera's raw image, because the Teach page cuts its training pictures from there.

## Connect the board { #connect }

<div class="ipro-steps" markdown>

1. **Plug in USB-C**: a camera and a serial port named **IPRO7 UVC Cam** appear on the computer. If they do not, the board is not in `image` mode; go on to the next step.

2. **Open the Teach page**: click **Teach** in Studio's rail (Command+5 on macOS, Ctrl+5 on Windows). If the board is in another mode, the top of the page shows `The Reef is in … mode.` and **Switch to Teach**; press it and wait for the board to restart (about 2 s). You can also type `mode image` on the console.

3. **Check the camera view**: the **Camera** area shows the Reef's camera with a green box in the middle. Before any image model is deployed, the top of the view shows `IPRO AI TEACH` and `NO MODEL`.

4. **Check the status**: **Board** in the status row shows `on USB`; the **Put it on the board** area shows what the board runs, for example `Board found, no model on it yet.` or `Running 3 classes: …`.

</div>

## The Teach page { #page-layout }

| Area | What it holds |
|---|---|
| Status row | **Board** (`on USB` when the board is found), **Crops** (pictures collected), **Held-out accuracy** (score on held-out crops), **Last deploy** (how long the last deploy took) |
| **Camera** | The Reef's camera view. The green box is what the model sees; outside it is the result the board draws. **Mirror** at the bottom left only mirrors the preview, never the training; off by default |
| **Hold to record** | Hold to record the selected class at 5 crops a second; release to stop. The button names the class, for example **Hold to record CLASS 1** |
| **Classes** | The class list. Each row has the name, the crop count, the latest thumbnails, **Review** (look through the crops and drop bad ones), **Clear** (drop every crop of the class) and **Remove** (delete the class; BACKGROUND cannot be removed). Above the list: **Open…**, **Save…**, **+ Add class** |
| **Train** | The backbone menu and the **Train** button; the training result appears below |
| **Put it on the board** | The model on the board and the **Deploy** button; deploy progress appears below |

## Create classes and record { #collect }

<div class="ipro-steps" markdown>

1. **Name the classes**: the list starts with **BACKGROUND**, **CLASS 1** and **CLASS 2**. Click a name to rename it; press **+ Add class** for more, up to 8 classes. Names may use letters, digits, spaces, underscores, hyphens and periods, up to 15 characters, and Studio turns them to upper case. The board draws names in its built-in bitmap font, which has no Chinese characters.

2. **Record BACKGROUND**: select **BACKGROUND**, keep the box empty, and hold **Hold to record** for a few seconds. This class lets the board say "nothing there"; always record it.

3. **Record each object**: select a class, put the object in the box, and hold **Hold to record** for a few seconds. While recording, the box on the preview turns red and shows `REC` and the class name; the number next to the class is its crop count.

4. **Check the crops**: after each class, press **Review** and drop bad crops, for example where the object is half out of the box. To record a class again from scratch, press **Clear**.

</div>

Tips for recording:

- Bring small objects close to the lens so they fill most of the box.
- Turn the object slowly and move it closer and farther while recording, so the model sees different angles and distances. Two classes that look alike may be confused at some angles; record more at those angles.
- Record in the light and against the background you will use. Training adds a mirrored copy and two brightness changes of every crop by itself; you need not record mirrored views.
- The preview is not mirrored by default: you see what the camera sees. To move it like a mirror, tick **Mirror**; it does not affect training.

## Train { #train }

<div class="ipro-steps" markdown>

1. **Choose a backbone** in the **Train** menu (table below). The default is MobileNetV2 0.35.

2. **Press Train**: training runs on the computer's CPU and usually takes a few seconds. At least two classes need crops, otherwise the page says `Record at least two classes, then train.`; classes without crops are skipped.

3. **Read the result**: `Trained in <seconds> s: <percent> of held-out crops right`, and **Held-out accuracy** in the status row updates.

</div>

One crop in every four of each class is held out of training and used to score the model afterwards: that is **Held-out accuracy**. Crops from one recording look alike, so the score says the classes can be told apart, not that a new scene will be right. With too few crops to hold any out, the page says `Too few crops to hold any out for checking.`

If the result says `<A> taken for <B> (<n>x)`, n crops of class A were classified as B - usually because the object left the box while recording. Press **Review** on both classes, drop those crops and train again.

| Menu option | Character | Model size |
|---|---|---|
| MobileNetV2 0.35 (default) | More accurate | 461 KB |
| MobileNetV1 0.25 | Faster, about half the size | 237 KB |

The NPU times in the menu are approximate. INTELPRO measured about 10.5 ms per run for MobileNetV2 0.35 on the board's NPU with Edge AI firmware 2.0.0.

## Deploy { #deploy }

<div class="ipro-steps" markdown>

1. **Check the board**: the **Put it on the board** area has found the board and shows the classes it runs, or `Board found, no model on it yet.`

2. **Press Deploy**: Studio runs three steps and ticks each one: **Compile the model**, **Send and write**, **Restart the board**.

3. **Wait for the camera**: the camera view goes away while the board restarts and shows `Deploying… the camera comes back when the board does.` This is normal; the camera comes back by itself.

4. **Check that it finished**: `On the board in <seconds> s` and `It now recognises …` with the classes the board now knows.

</div>

The board checks a model before writing it. If it refuses one, the model already on the board is untouched and you can deploy again straight away. If power or the cable is cut while writing, the image tool - which has a single slot - is left without a model and the camera view shows `NO MODEL: DEPLOY INTERRUPTED`; deploy again.

## See the result on the board { #run }

After the deploy, put an object in the box. The board's NPU classifies it live and draws the result on the camera stream:

| Where | What |
|---|---|
| Top | `IPRO AI TEACH`, the NPU time per run and runs per second |
| Left of the box | The top class and its confidence |
| Right of the box | Every class's probability; the top one in green |
| Bottom | The number of classes in the model, for example `3 CLASSES` |

The Reef draws this into its own USB camera stream, so any program that can open a USB camera shows it, not only Studio.

You can also check the state on the console:

| Command | What it does |
|---|---|
| `teach` | Model state, class list with live probabilities, NPU rate, USB connection |
| `teach print on` / `teach print off` | Print every result on the console |
| `teach mirror on` / `teach mirror off` | Mirror the camera stream the board sends (off by default; the Teach page needs the camera's own orientation, so normally leave it off) |
| `teach dump` | Dump the 128×128 input currently fed to the NPU |

## Verify { #verify }

1. With each class's object in the box, its name shows left of the box, and its probability on the right is the highest and in green.
2. With the box empty, the result is **BACKGROUND**.
3. The class count at the bottom of the view matches the Teach page.
4. After unplugging USB-C or a restart, the model is still on the board: the view no longer shows `NO MODEL`, and **Put it on the board** shows `Running <n> classes: …`.

## Add samples and retrain { #iterate }

The training score only says the collected crops can be told apart. Test in the real scene; where the board gets it wrong, record more at that angle or in that light, then train and deploy again:

1. Select the class that was misread, hold **Hold to record** at the angle and light where it went wrong, and press **Review** to drop bad crops if needed.
2. Press **Train**. After the classes or crops change, the training area says `The crops changed since training. Train again.`
3. Press **Deploy**.

Keep and reuse what you collected:

- **Save…**: choose a folder; Studio writes one sub-folder per class with the crops as PNG files.
- **Open…**: open a folder of the same layout (one sub-folder per class, `.png` or `.jpg`) to add samples or retrain without collecting again. 128×128 pictures are used as crops; other sizes are treated as camera frames and the center box is cut out. Folder names become class names.
- The same folder can be trained from the command line, without the window, into a model package and deployed:

    ```bash
    ipro-ai train image <folder> --out cups.ipkg --backbone mnv2_035
    ipro-ai deploy cups.ipkg --switch
    ```

    `--backbone` is `mnv2_035` (MobileNetV2 0.35) or `mnv1_025` (MobileNetV1 0.25).

## Specifications { #specs }

| Item | Specification |
|---|---|
| Camera stream (USB camera) | 640×360 MJPEG, USB Full-Speed |
| Model input | The center box (x 192-447, y 52-307 of the preview), scaled to 128×128 RGB |
| Classes | 2 to 8 (BACKGROUND included) |
| Class names | Up to 15 characters: upper-case letters, digits, space, underscore, hyphen and period |
| Training | Frozen MobileNet backbone, last layer only, on the computer's CPU |
| Model | MobileNetV2 0.35 (461 KB, all 63 layers on the NPU) or MobileNetV1 0.25 (237 KB) |
| NPU time on the board | About 10.5 ms for MobileNetV2 0.35; model load about 0.74 s |
| Model slot | Image model slot, 508 KB of room |

## Tips { #tips }

- **Always have a BACKGROUND class.** Without it, the board still picks one of the known classes when the box is empty.
- **Image recognition has no "I don't know" answer.** An object it was not taught goes to the most similar class, possibly with high confidence. For other objects that will appear in view, add a class (for example OTHER) and record them.
- Only what is inside the box counts; an object that is only outside the box is not recognized.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| No **IPRO7 UVC Cam** in the camera list; Studio says `No board with the Teach firmware on USB.` | The board is not in `image` mode, does not run the Edge AI firmware, or the cable is charge-only | Press **Switch to Teach** on the Teach page or type `mode image` on the console; use a data cable |
| The Camera area keeps showing `Looking for the IPRO7 UVC Cam…` | As above | As above |
| On macOS the Camera area shows a camera-permission message | IPRO AI Studio has no camera permission | See [Operating-system permissions](install.md#permissions) |
| On macOS no program shows the camera | Another program still holds the camera | Quit that program, then unplug and replug USB-C |
| The console repeats `no camera answers` | The camera is not connected, or SW7 is not at CAM | Unplug USB-C, check the camera cable, set SW7 to CAM |
| The view shows `NO MODEL: NO MODEL IN MFG` | No image model deployed yet | Train, then press **Deploy** |
| The view shows `NO MODEL: DEPLOY INTERRUPTED` | The last deploy did not finish | Deploy again |
| The view shows `NO MODEL: WRONG MODEL` | The slot holds another kind of model | Deploy once more |
| The Camera area shows `The board went away. Waiting for it…` | The board is restarting (after a deploy or a mode switch), or USB-C was unplugged | Normal after a deploy; the camera comes back by itself. If not, unplug and replug USB-C |
| The training result says `<A> taken for <B>` | The object left the box while recording | Press **Review** on both classes, drop bad crops, train again |
| In real use one class is often read as another | Not enough data at some angles or light, or the two look alike | Record more at those angles and in that light, then train and deploy |
| An object class is reported with the box empty | No BACKGROUND class, or too little of it | Record BACKGROUND, train and deploy again |

For anything else, see [Troubleshooting](troubleshooting.md).

## Next steps { #next-steps }

- [Voiceprint Recognition](voice.md): teach the same Reef who is speaking.
- [Image Teach in the Browser](browser.md): the same flow in Chrome or Edge, without Studio.
