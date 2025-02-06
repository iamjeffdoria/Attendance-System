

$(document).ready(function () {
  $('#addSubjectForm').submit(function (e) {
    e.preventDefault();

    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var formData = {
      'name': $('#name').val(),
      'description': $('#description').val(),
    };

    $.ajax({
      type: "POST",
      url: "{% url 'add_subject' %}",
      data: JSON.stringify(formData),  
      contentType: 'application/json', 
      headers: {"X-CSRFToken": csrftoken},
      success: function (response) {
        if (response.status === "success") {
          $('#message').html('<div class="alert alert-primary alert-dismissible fade show" role="alert"><i class="bi bi-star me-1"></i>' + response.message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
           $('#verticalycentered').modal('hide');
          $('#addSubjectForm')[0].reset();
          setTimeout(function(){
            location.reload();
          },500);
        } else {
          $('#message').html('<div class="alert alert-danger alert-dismissible fade show" role="alert"><i class="bi bi-exclamation-triangle me-1"></i>' + response.message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
        }
     
      },
      error: function () {
        $('#message').html('<div class="alert alert-danger alert-dismissible fade show" role="alert"><i class="bi bi-exclamation-triangle me-1"></i>Something went wrong. Please try again later.<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
      }
    });
    setTimeout(function() {
        $('.alert').fadeOut(500, function () { $(this).remove(); });
      }, 3000);
  });
});
console.log("JS IS CONNECTED!")