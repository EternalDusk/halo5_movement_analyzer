using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using Newtonsoft.Json.Linq;
using UnityEngine.UI;

public class DataPlayer : MonoBehaviour
{
    public string filename;
    public string jsonlFilePath;
    public Slider scrubSlider;

    public GameObject playerCapsule;
    public RawImage displayImage;
    public Text controllerText;
    public Text frameText;

    private List<long> frameOffset = new List<long>();
    private FileStream fileStream;
    private StreamReader reader;

    public float timer = 0f;
    public float frameRate = 120f;
    public int currentFrame = 0;

    public int totalFrames;
    private bool isScrubbing = false;

    // Start is called before the first frame update
    void Start()
    {
        jsonlFilePath = Path.Combine(Application.streamingAssetsPath, filename);
        fileStream = new FileStream(jsonlFilePath, FileMode.Open, FileAccess.Read);
        
        Debug.Log("Indexing file...");
        IndexFile();

        totalFrames = frameOffset.Count;
        scrubSlider.maxValue = totalFrames - 1;
        scrubSlider.onValueChanged.AddListener(OnScrub);
    }


    // Update is called once per frame
    void Update()
    {
        if (isScrubbing) return;

        timer += Time.deltaTime;
        if (timer >= 1f / frameRate)
        {
            timer = 0f;
            LoadFrame(currentFrame);
            currentFrame = (currentFrame + 1) % totalFrames;
            scrubSlider.value = currentFrame;
        }
    }

    private void IndexFile()
    {
        frameOffset.Clear();
        fileStream.Seek(0, SeekOrigin.Begin);

        using (var binReader = new BinaryReader(fileStream, System.Text.Encoding.UTF8, leaveOpen: true))
        {
            long pos = 0;
            while (fileStream.Position < fileStream.Length)
            {
                frameOffset.Add(pos);
                string line = ReadLine(binReader);
                pos = fileStream.Position;
            }
        }

        fileStream.Seek(0, SeekOrigin.Begin);
        reader = new StreamReader(fileStream, System.Text.Encoding.UTF8, false, 1024, leaveOpen: true);
    }

    private string ReadLine(BinaryReader reader)
    {
        var line = new List<byte>();
        while (true)
        {
            if (reader.BaseStream.Position >= reader.BaseStream.Length)
                break;
            
            byte b = reader.ReadByte();
            if (b == '\n') break;
            line.Add(b);
        }
        return System.Text.Encoding.UTF8.GetString(line.ToArray()).TrimEnd('\r');
    }

    void OnScrub(float val)
    {
        isScrubbing = true;
        currentFrame = Mathf.FloorToInt(val);
        LoadFrame(currentFrame);
        isScrubbing = false;
    }

    void LoadFrame(int frameIndex)
    {
        if (frameIndex < 0 || frameIndex >= totalFrames) return;

        reader.DiscardBufferedData(); // reset internal buffer
        fileStream.Seek(frameOffset[frameIndex], SeekOrigin.Begin);
        string line = reader.ReadLine();

        if (string.IsNullOrWhiteSpace(line)) return;

        JObject json;
        try
        {
            json = JObject.Parse(line);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Exception caught: {e.GetType().Name} - {e.Message}\n{e.StackTrace}");
            return;
        }

        var mem = json["memory"];
        var inputs = json["inputs"];
        var imgB64 = (string)json["image"];

        Vector3 pos = new Vector3(
            (float)mem["x"],
            (float)mem["y"],
            (float)mem["z"]
        );

        float pitch = (float)mem["pitch"] * -90f;
        float yaw = (float)mem["yaw"] * -Mathf.Rad2Deg + 90f;

        byte[] imgBytes = System.Convert.FromBase64String(imgB64);
        Texture2D tex = new Texture2D(2, 2);
        tex.LoadImage(imgBytes);

        playerCapsule.transform.position = pos;
        playerCapsule.transform.rotation = Quaternion.Euler(pitch, yaw, 0);
        displayImage.texture = tex;
        controllerText.text = inputs.ToString();
        frameText.text = mem.ToString();
    }

    void OnDestroy()
    {
        reader?.Close();
        fileStream?.Close();
    }

    class FrameData
    {
        public Vector3 pos;
        public float yaw;
        public float pitch;
        public Texture2D image;
        public string controllerInput;
        public string memText;
    }
}
