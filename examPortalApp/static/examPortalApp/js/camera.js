
  var width = 320; // We will scale the photo width to this
  var height = 0; // This will be computed based on the input stream

  var streaming = false;

  var videoEl = null;
  var canvas = null;
  var photo = null;
  var startbutton = null;

  function camStartup() {
    console.log("camStartup");
    videoEl = document.getElementById('video');
    canvas = document.getElementById('canvas');
    photo = document.getElementById('photo');
    startbutton = document.getElementById('startbutton');

    // navigator.mediaDevices.getUserMedia({
    //     video: {
    //       facingMode: 'environment',
    //     },
    //     audio: false
    //   })
    //   .then(function(stream) {
    //     videoEl.srcObject = stream;
    //     videoEl.play();
    //     document.getElementById('close-cam-btn').onclick=()=>{
    //       videoEl.pause();
    //       stream.getTracks().forEach(function(track) {
    //         track.stop();
    //       });
    //       closePopup(document.getElementById('close-cam-btn'));
    //     }
    //   })
    //   .catch(function(err) {
    //     console.error("An error occurred: " + err);
    //   });

    videoEl.addEventListener('canplay', function(ev) {
      if (!streaming) {
        height = videoEl.videoHeight / (videoEl.videoWidth / width);

        if (isNaN(height)) {
          console.log(videoEl.videoHeight);
          console.log(videoEl.videoWidth);
          height = width / (4 / 3);
        }

        videoEl.setAttribute('width', width);
        videoEl.setAttribute('height', height);
        canvas.setAttribute('width', width);
        canvas.setAttribute('height', height);
        photo.setAttribute('width', width);
        photo.setAttribute('height', height);
        streaming = true;
      }
    }, false);

    startbutton.addEventListener('click', function(ev) {
      takepicture();
      ev.preventDefault();
    }, false);

    clearphoto();
    // openCameraPopup();
  }


  function clearphoto() {
    var context = canvas.getContext('2d');
    context.fillStyle = "#AAA";
    context.fillRect(0, 0, canvas.width, canvas.height);

    var data = canvas.toDataURL('image/png');
    photo.setAttribute('src', data);
  }

  function takepicture() {
    var context = canvas.getContext('2d');
    if (width && height) {
      canvas.width = width;
      canvas.height = height;
      context.drawImage(video, 0, 0, width, height);

      var data = canvas.toDataURL('image/png');
      photo.setAttribute('src', data);
    } else {
        clearphoto();
    }
  }

  function uploadWebcamPicture() {
    var data = canvas.toDataURL('image/png');
    sendWebcamData(data);
  }
