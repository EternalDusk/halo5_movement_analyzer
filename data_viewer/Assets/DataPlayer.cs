using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using Newtonsoft.Json.Linq;
using UnityEngine.UI;

public class DataPlayer : MonoBehaviour
{
    public TextAsset jsonlFile;

    public GameObject playerCapsule;
    public RawImage displayImage;
    public Text controllerText;

    private List<FrameData> frames = new List<FrameData>();
    public int currentFrame = 0;
    public float timer = 0f;
    public float frameRate = 120f;

    // Start is called before the first frame update
    void Start()
    {
        frames.Clear();

        var lines = jsonlFile.text.Split('\n');
        foreach (var line in lines)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;
            var json = JObject.Parse(line);
            var mem = json["memory"];
            var inputs = json["inputs"];
            var imgB64 = (string)json["image"];

            FrameData frame = new FrameData();
            frame.pos = new Vector3(
                (float)mem["x"],
                (float)mem["y"],
                (float)mem["z"]);
            
            float pitch = (float)mem["pitch"] * 90f;
            float yaw = (float)mem["yaw"] * Mathf.Rad2Deg;
            frame.rot = Quaternion.Euler(pitch, yaw, 0);

            frame.controllerInput = inputs.ToString();

            // Decode base64 to texture
            byte[] imgBytes = System.Convert.FromBase64String(imgB64);
            Texture2D tex = new Texture2D(2, 2);
            tex.LoadImage(imgBytes);
            frame.image = tex;

            frames.Add(frame);
        }
    }

    // Update is called once per frame
    void Update()
    {
        if (frames.Count == 0) return;

        if (timer >= 1f / frameRate)
        {
            timer = 0f;
            ShowFrame(frames[currentFrame]);
            currentFrame = (currentFrame + 1) % frames.Count;
        } else {
            timer += Time.deltaTime; 
        }
    }

    void ShowFrame(FrameData frame)
    {
        playerCapsule.transform.position = frame.pos;
        playerCapsule.transform.rotation = frame.rot;

        displayImage.texture = frame.image;
        controllerText.text = frame.controllerInput;
    }

    class FrameData
    {
        public Vector3 pos;
        public Quaternion rot;
        public Texture2D image;
        public string controllerInput;
    }
}
