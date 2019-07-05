/*global google: false, $: false*/

/*
 * For each point that the user marks on the map,
 * create a pointer.
 *
 * If more than 2 pointers are available, trace
 * polylines through all pointers TODO of the same type
 *
 * Geolocation should be used to set the position
 * of the map.
 *
 * TODO Functionalities to track parking should also be implemented.
 */


$(function () {
  'use strict';
  var loggedProcessionId = null,
      loggedProcessionName = null;

  function init() {

    var $markerControls = $('#si-add-marker-controls'),
        $setTailControls = $('#si-set-tail-controls'),
        $markerControlButtons = $('button[data-si-action]'),
        $toast = $('#si-app-toast'),
        $btnFinishProcession = $('#btnFinishProcession');

    var map = new L.Map("si-map");
	var osmUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 19, attribution: osmAttrib});

	map.setView(new L.LatLng(39.603698, -8.414741),18);
	map.addLayer(osm);

	var LeafIcon = L.Icon.extend({
    options: {
        iconAnchor:   [12, 30],
    }
});

    var currentHeadIcon = new LeafIcon({iconUrl: 'img/markers/marker-head.png'}),
        nextTailIcon = new LeafIcon({iconUrl: 'img/markers/marker-middle.png'}),
        currentTailIcon = new LeafIcon({iconUrl: 'img/markers/marker-tail.png'}),
        deviceIcon = new LeafIcon({iconUrl: 'img/markers/marker-device.png'})

    var markers = {
          currentHead: L.marker([0, 0], {icon: currentHeadIcon}).addTo(map),
          nextTail: L.marker([0, 0], {icon: nextTailIcon}).addTo(map),
          currentTail: L.marker([0, 0], {icon: currentTailIcon}).addTo(map)
        }

    var location_markers = []

    var processionPath = L.polyline([], {color: '#FF0000',
                                         opacity: 1.0,
                                         weight:4}
                                    ).addTo(map);

    var processionPath_ios = L.polyline([], {color: '#00FF00',
                                         opacity: 1.0,
                                         weight:2}
                                    ).addTo(map);
    var expectedProcessionRoute = L.polyline([], {color: '#000000',
                                                  opacity: 0.4,
                                                  weight:4}
                                             ).addTo(map);

    var addPointInfoWindow = L.popup()
                                    .setLatLng([0, 0])
                                    .setContent($markerControls[0])
                                    //.openOn(map);
    var setTailPointWindow = L.popup()
                                    .setLatLng([0, 0])
                                    .setContent($setTailControls[0])
                                    //.openOn(map);





    function getExpectedCoordsForProcession() {
      return $.ajax({
        url: '/web/expectedroute',
        type: 'get',
        dataType: 'json',
        data: { id: loggedProcessionId }
      })
      .done(function (positions) {
        expectedProcessionRoute.setLatLngs(positions);

        //centar o caminho no mapa quando não há permissão de localização
        navigator.geolocation.watchPosition(function(position) {},
                                          function(error) {
                                            map.fitBounds(expectedProcessionRoute.getBounds());
                                          });
      });
    }

    function getDevicesLocation() {
      return $.ajax({
        url: '/web/get_tracker_locations',
        type: 'get',
        dataType: 'json',
        data: { }
      })
      .done(function (positions) {
        location_markers.forEach(function(location_marker) {
                map.removeLayer(location_marker)
            });
          location_markers = [];
         positions.forEach(function(position) {
                location_markers.push(L.marker([position.position.lat, position.position.lng], {icon: deviceIcon}).bindTooltip(position.device_id,
                    {
                permanent: true,
                direction: 'right'
            }).addTo(map))
            });
      });
    }

    function getCoordinatesForCurrentProcession() {
      return $.ajax({
        url: '/web/processionposition',
        type: 'get',
        dataType: 'json',
        data: { id: loggedProcessionId }
      });
    }

    function getCoordinatesForCurrentProcession_ios() {
      return $.ajax({
        url: '/web/processionposition_ios',
        type: 'get',
        dataType: 'json',
        data: { id: loggedProcessionId }
      });
    }

    function openToast(type, message) {
      type = type === 'error' ? 'danger' : type;

      // Remove error and success classes.
      $toast
        .text(message)
        .removeClass('alert-danger')
        .removeClass('alert-success')
        .addClass('alert-' + type)
        .removeClass('hidden');

      setTimeout(function () {
        $toast.addClass('hidden');
      }, 2000);
    }

    function updateLineAndMarkers() {
        try {
           getDevicesLocation();
        }
        catch (e) {

        }


      getCoordinatesForCurrentProcession_ios()
        .done(function (data) {
          if (!data.length) { return; }
          processionPath_ios.setLatLngs(data.map(function (p) {
            return p.position;
          }))
          ;

        })
        .error(function () {
          openToast('error', 'Ocorreu um erro ao atualizar as posições da procissão IOS.');
        });


      return getCoordinatesForCurrentProcession()
        .done(function (data) {
          if (!data.length) { return; }

          markers.currentHead.setLatLng(data[data.length - 1].position);

          if (data.length > 2) {
            markers.nextTail.setLatLng(data[1].position);
          } else {
            markers.nextTail.setLatLng([0, 0]);
          }

          if (data.length > 1) {
            markers.currentTail.setLatLng(data[0].position);
          } else {
            markers.currentTail.setLatLng([0, 0]);
          }

          processionPath.setLatLngs(data.map(function (p) {
            return p.position;
          }))
          ;

        })
        .error(function () {
          openToast('error', 'Ocorreu um erro ao atualizar as posições da procissão.');
        });
    }

    function openInfoWindowForTailPoint() {
      setTailPointWindow
        .setLatLng(markers.nextTail.getLatLng());

      setTailPointWindow.openOn(map);
      map.closePopup(addPointInfoWindow);
    }

    /**
     * @param {string} type
     * @param {google.maps.LatLng} position
     * @param {function} cb
     */
    function uploadPosition(spec) {
      spec.id = loggedProcessionId;

      return $.ajax({
        type: 'post',
        url: '/web/procession',
        contentType: 'application/json',
        data: JSON.stringify(spec)
      });
    }

    function FinishProcession() {
      var spec = {id: loggedProcessionId}
      return $.ajax({
        type: 'post',
        url: '/web/processionFinish',
        contentType: 'application/json',
        data: JSON.stringify(spec)
      }).done(function () {
      map.closePopup(addPointInfoWindow);
      map.closePopup(setTailPointWindow);
      processionPath.setLatLngs([]);
      processionPath_ios.setLatLngs([]);
      markers.currentHead.setLatLng([0, 0]);
      markers.currentTail.setLatLng([0, 0]);
      markers.nextTail.setLatLng([0, 0]);
      });



    }

    function openAddPointWindow(e) {
        if (typeof(e.latlng) != 'undefined' && e.latlng != null)
        {
             var latLng = e.latlng,
                  latLngJson = JSON.stringify({
                    lat: latLng.lat,
                    lng: latLng.lng
                  });

              addPointInfoWindow.setLatLng(latLng);

              for (var i = 0, len = $markerControlButtons.length; i < len; i++) {
                $markerControlButtons[i].setAttribute('data-si-coords', latLngJson);
              }

              map.closePopup(setTailPointWindow);
              addPointInfoWindow.openOn(map);
        }

    }

    function onAddPointButtonClicked() {
      var spec = null,
          $button = $(this),
          action = $button.attr('data-si-action'),
          coords = JSON.parse($button.attr('data-si-coords')),
          pPoint = $button.attr('point');
      map.closePopup(addPointInfoWindow);

      if (action !== 'commit') {
        return;
      }

      var latLng = L.latLng(coords.lat, coords.lng);
        if (typeof(latLng) != 'undefined' && latLng != null)
        {
              $markerControlButtons.attr('disabled', 'true');

              spec = {
                position: {
                  lat: latLng.lat,
                  lng: latLng.lng
                },
                processionPoint: pPoint
              };

              uploadPosition(spec)
                .always(function () {
                  map.closePopup(addPointInfoWindow);
                  $markerControlButtons.removeAttr('disabled');
                })
                .done(function () {
                  openToast('success', 'Coordenada adicionada com sucesso.');
                  return updateLineAndMarkers();
                })
                .error(function () {
                  openToast('error', 'Ocorreu um erro ao enviar a nova coordenada. Tente novamente.');
                });
        }
    }

    function onSetTailPointClicked() {
      var latLng = markers.nextTail.getLatLng(),
          $button = $(this);
      if (typeof(latLng) != 'undefined' && latLng != null)
        {
              map.closePopup(setTailPointWindow);

              if ($button.attr('data-si-action') !== 'commit') {
                return;
              }

              uploadPosition({
                position: {
                  lat: latLng.lat,
                  lng: latLng.lng
                },
                processionPoint: 'tail'
              })
              .done(function () {
                openToast('success', 'O ponto de cauda foi marcado com sucesso.');
                return updateLineAndMarkers();
              })
              .error(function () {
                openToast('error', 'Ocorreu um erro ao marcar o ponto de cauda.');
              });
      }
    }

    // Wire-up events to show an info window whenever the user clicks
    // on the map.
    //google.maps.event.addListener(map, 'click', openAddPointWindow);


    map.on('click', openAddPointWindow);


    $markerControls.on('click', '[data-si-action]', onAddPointButtonClicked);

    $setTailControls.on('click', '[data-si-action]', onSetTailPointClicked);

    markers.nextTail.on('click', openInfoWindowForTailPoint)

    $btnFinishProcession.on('click', FinishProcession);


    /*google.maps.event.addListener(
      markers.nextTail,
      'click',
      openInfoWindowForTailPoint
    );*/

    //map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(
    //  document.getElementById('si-legend'));

    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function (map) {
                                    return document.getElementById('si-legend');
                                    };

    legend.addTo(map);

    $('#si-procession-name').text(loggedProcessionName);

    // Refresh the coordinates for the current procession every 10 s.
    getExpectedCoordsForProcession()
      .then(updateLineAndMarkers)
      .then(function () {
        setInterval(updateLineAndMarkers, 2000);
      });

    function setMapCenterWithGeolocation(position) {
      var pos = new L.LatLng(
        position.coords.latitude,
        position.coords.longitude);
      map.panTo(pos);
    }

    // If we get access to geolocation, make use of it to update the
    // center of the map every minute to the person's current position.
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function onSuccessfulCoords(pos) {
        setMapCenterWithGeolocation(pos);

        setInterval(function () {
          navigator.geolocation.getCurrentPosition(setMapCenterWithGeolocation);
        }, 60000); // 1 minute
      });
    }
  }

  $('#si-procession-selector').on('change', function onProcessionIdChanged() {
    var value = $(this).val();

    if (!value) {
      $('#si-start-app').attr('disabled', 'true');
    } else {
      $('#si-start-app').removeAttr('disabled');
      loggedProcessionId = value;
      loggedProcessionName = 'Procissão: ' + $(this).find('[value="' + value + '"]').text();
    }
  });

  $.ajax({
    url: '/web/routesummary',
    dataType: 'json'
  })
  .done(function (routes) {
    var $routeSelector = $('#si-procession-selector');

    $routeSelector.empty();

    $('<option value="" selector>Selecione...</option>')
      .appendTo($routeSelector);

    routes.map(function (route) {
      $('<option value="' + route.id + '">' + route.name + '</option>')
        .appendTo($routeSelector);
    });
  });

  $('#si-start')
    .on('hidden.bs.modal', init)
    .modal('show');
});
