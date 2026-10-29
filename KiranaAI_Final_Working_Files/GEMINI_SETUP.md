# Gemini API setup and verification

1. Obtain a private Gemini API key from https://aistudio.google.com/api-keys.
2. In the app, expand **API Configuration**, enter the key, and leave **Force offline parser** unchecked.
3. Process a new message (not one of the preset demos), such as: `Bhai 4 packets Maggi 70g aur Tata namak 1kg ke 2 packs bhej dena`.
4. Verify the engine status says **Gemini gemini-3.5-flash-lite (live API)** or **Gemini gemini-3.8-flash (live API)**. An offline fallback result is not a successful Gemini run.
5. The expected order contains MAG001 × 4 packs and TSL002 × 2 packs, total ₹120. These values are catalog-validated independently of Gemini.

Default model is `gemini-3.5-flash-lite`. If it returns 404, the application tries `gemini-3.8-flash` once. Other API errors are reported in the UI by HTTP status and the offline parser handles the message. Actual live requests are not verified in this package because no private API key was available during testing.

Override using `GEMINI_MODEL` and optionally `GEMINI_404_FALLBACK_MODEL` in the local `.env`, or by setting environment variables. Restart the app after changing them. Do not commit keys into code or shared ZIPs.

If **both** models return 404, check the complete error message in your local PowerShell log (redact any secrets before sharing). A 404 can also indicate project restrictions or unsupported model versions. Check your project's access and selected model using Google AI Studio.
