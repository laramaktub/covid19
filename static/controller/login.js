var submitted = false;

function isChecked() {
  document.getElementById("terms").checked; 
}
function checkTerms() {
  document.getElementById('error').style.visibility = !document.getElementById("terms").checked && this.submitted ? "visible" : "hidden";
}
function onLogin() {
  if (document.getElementById("terms").checked) {
    document.location.href = "/start"
  }
  else {
    document.getElementById('error').style.visibility = "visible"
  }
  this.submitted = true;
}
