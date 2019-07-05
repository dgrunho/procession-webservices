$(function () {
  var $parkingForm = $('#parking-form'),
      $lastUpdate = $('#last-update'),
      $parkList = $('#park-list');

  function setDisabledOnForm(disabled) {
    if (disabled) {
      $parkingForm.find('button, select').attr('disabled', 'true');
    } else {
      $parkingForm.find('button, select').removeAttr('disabled');
    }
  }

  $.ajax({
    type: 'get',
    dataType: 'json',
    url: '/web/parkingget'
  })
  .done(function (parkingData) {

    $parkList.empty();
    parkingData.forEach(function (park) {
      $('<option value="' + park.id + '">' + park.name + '</option>')
        .appendTo($parkList);
    })

    setDisabledOnForm(false);
  })
  .error(function () {
    $parkList.empty();
    $('<option value="">Ocorreu um erro ao obter os parques.</option>');
  });

  $('#allocation').on('click', '[name=allocation]', function (e) {
    var $button = $(this);

    e.preventDefault();

    setDisabledOnForm(true);

    $.ajax({
      type: 'post',
      url: '/web/parkingupdate',
      contentType: 'application/json',
      data: JSON.stringify({
        id: $parkList.val(),
        allocation: $button.val()
      })
    })
    .done(function () {
      $('#success-msg').removeClass('hidden');
      $lastUpdate.text((new Date()).toLocaleString());

      setTimeout(function () {
        $('#success-msg').addClass('hidden');
        setDisabledOnForm(false);
      }, 5000);
    })
    .error(function (err) {
      $('#error-msg').removeClass('hidden');

      setTimeout(function () {
        $('#error-msg').addClass('hidden');
        setDisabledOnForm(false);
      }, 5000);
    })
  });
});
