# ... (bestehender Import-Block bleibt unverändert)

# =====================================
# F5-TTS
# =====================================

def segments_f5_tts(filtered_f5_segments, TRANSLATE_AUDIO_TO, f5_host="http://localhost:5000"):
    """
    Synthesize speech with F5-TTS via HTTP-API.
    Assumes F5-TTS runs in Docker and is reachable on localhost:5000.
    """
    import requests

    for segment in tqdm(filtered_f5_segments["segments"]):
        speaker = segment["speaker"]
        text = segment["text"]
        start = segment["start"]
        tts_name = segment.get("tts_name", "")

        filename = f"audio/{start}.ogg"
        logger.info(f"{text} >> {filename}")

        try:
            payload = {
                "text": text,
                "lang": TRANSLATE_AUDIO_TO
            }
            # <optional> Pass speaker/model if F5-TTS supports it via API
            if tts_name and tts_name != "F5-TTS":
                payload["voice"] = tts_name

            response = requests.post(f"{f5_host}/api/tts", json=payload)
            response.raise_for_status()
            # Save as OGG or WAV (F5 liefert OGG/WAV, ggf. anpassen)
            with open(filename, "wb") as fout:
                fout.write(response.content)

            verify_saved_file_and_size(filename)
        except Exception as error:
            error_handling_in_tts(error, segment, TRANSLATE_AUDIO_TO, filename)

# ... (restlicher Code bleibt unverändert)

def audio_segmentation_to_voice(
    result_diarize,
    TRANSLATE_AUDIO_TO,
    is_gui,
    tts_voice00,
    tts_voice01="",
    tts_voice02="",
    tts_voice03="",
    tts_voice04="",
    tts_voice05="",
    tts_voice06="",
    tts_voice07="",
    tts_voice08="",
    tts_voice09="",
    tts_voice10="",
    tts_voice11="",
    dereverb_automatic=True,
    model_id_bark="suno/bark-small",
    model_id_coqui="tts_models/multilingual/multi-dataset/xtts_v2",
    delete_previous_automatic=True,
):

    remove_directory_contents("audio")

    speaker_to_voice = {
        "SPEAKER_00": tts_voice00,
        "SPEAKER_01": tts_voice01,
        "SPEAKER_02": tts_voice02,
        "SPEAKER_03": tts_voice03,
        "SPEAKER_04": tts_voice04,
        "SPEAKER_05": tts_voice05,
        "SPEAKER_06": tts_voice06,
        "SPEAKER_07": tts_voice07,
        "SPEAKER_08": tts_voice08,
        "SPEAKER_09": tts_voice09,
        "SPEAKER_10": tts_voice10,
        "SPEAKER_11": tts_voice11,
    }

    for segment in result_diarize["segments"]:
        if "speaker" not in segment:
            segment["speaker"] = "SPEAKER_00"
            logger.warning(
                "NO SPEAKER DETECT IN SEGMENT: First TTS will be used in the"
                f" segment time {segment['start'], segment['text']}"
            )
        segment["tts_name"] = speaker_to_voice[segment["speaker"]]

    pattern_edge = re.compile(r".*-(Male|Female)$")
    pattern_bark = re.compile(r".* BARK$")
    pattern_vits = re.compile(r".* VITS$")
    pattern_coqui = re.compile(r".+\.(wav|mp3|ogg|m4a)$")
    pattern_vits_onnx = re.compile(r".* VITS-onnx$")
    pattern_openai_tts = re.compile(r".* OpenAI-TTS$")
    pattern_f5 = re.compile(r".* F5-TTS$")  # NEU

    all_segments = result_diarize["segments"]

    speakers_edge = find_spkr(pattern_edge, speaker_to_voice, all_segments)
    speakers_bark = find_spkr(pattern_bark, speaker_to_voice, all_segments)
    speakers_vits = find_spkr(pattern_vits, speaker_to_voice, all_segments)
    speakers_coqui = find_spkr(pattern_coqui, speaker_to_voice, all_segments)
    speakers_vits_onnx = find_spkr(pattern_vits_onnx, speaker_to_voice, all_segments)
    speakers_openai_tts = find_spkr(pattern_openai_tts, speaker_to_voice, all_segments)
    speakers_f5 = find_spkr(pattern_f5, speaker_to_voice, all_segments)  # NEU

    filtered_edge = filter_by_speaker(speakers_edge, all_segments)
    filtered_bark = filter_by_speaker(speakers_bark, all_segments)
    filtered_vits = filter_by_speaker(speakers_vits, all_segments)
    filtered_coqui = filter_by_speaker(speakers_coqui, all_segments)
    filtered_vits_onnx = filter_by_speaker(speakers_vits_onnx, all_segments)
    filtered_openai_tts = filter_by_speaker(speakers_openai_tts, all_segments)
    filtered_f5 = filter_by_speaker(speakers_f5, all_segments)  # NEU

    if filtered_edge["segments"]:
        logger.info(f"EDGE TTS: {speakers_edge}")
        segments_egde_tts(filtered_edge, TRANSLATE_AUDIO_TO, is_gui)
    if filtered_bark["segments"]:
        logger.info(f"BARK TTS: {speakers_bark}")
        segments_bark_tts(filtered_bark, TRANSLATE_AUDIO_TO, model_id_bark)
    if filtered_vits["segments"]:
        logger.info(f"VITS TTS: {speakers_vits}")
        segments_vits_tts(filtered_vits, TRANSLATE_AUDIO_TO)
    if filtered_coqui["segments"]:
        logger.info(f"Coqui TTS: {speakers_coqui}")
        segments_coqui_tts(
            filtered_coqui,
            TRANSLATE_AUDIO_TO,
            model_id_coqui,
            speakers_coqui,
            delete_previous_automatic,
            dereverb_automatic,
        )
    if filtered_vits_onnx["segments"]:
        logger.info(f"PIPER TTS: {speakers_vits_onnx}")
        segments_vits_onnx_tts(filtered_vits_onnx, TRANSLATE_AUDIO_TO)
    if filtered_openai_tts["segments"]:
        logger.info(f"OpenAI TTS: {speakers_openai_tts}")
        segments_openai_tts(filtered_openai_tts, TRANSLATE_AUDIO_TO)
    if filtered_f5["segments"]:
        logger.info(f"F5-TTS: {speakers_f5}")
        segments_f5_tts(filtered_f5, TRANSLATE_AUDIO_TO)  # NEU

    [result.pop("tts_name", None) for result in result_diarize["segments"]]
    return [
        speakers_edge,
        speakers_bark,
        speakers_vits,
        speakers_coqui,
        speakers_vits_onnx,
        speakers_openai_tts,
        speakers_f5,  # NEU
    ]