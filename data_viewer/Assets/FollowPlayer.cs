using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FollowPlayer : MonoBehaviour
{
    public Transform target;
    public Vector3 positionOffset;
    public Vector3 rotationOffset;
    public float lerpSpeed = 5f;

    // Update is called once per frame
    void Update()
    {
        Vector3 desiredPosition = target.position + positionOffset;
        transform.position = Vector3.Lerp(transform.position, desiredPosition, Time.deltaTime * lerpSpeed);
        
        transform.rotation = Quaternion.Euler(rotationOffset);
    }
}
