function previewImage() {
  const input = document.getElementById('imageInput');
  const image = document.getElementById('profileImage');

  if (input.files && input.files[0]) {
    const reader = new FileReader();

    reader.onload = function (e) {
      image.src = e.target.result;
    };
    reader.readAsDataURL(input.files[0]);
  }
}
