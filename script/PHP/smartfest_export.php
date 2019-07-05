<?php

$servername = "cp89.webserver.pt";
$username = "tabuleir_osUser";
$password = "tomar2019#%";
$dbname = "tabuleir_tabuleiros_db";

$ws_username = "mobile";
$ws_password = "mobile_tabuleiros_2015";
//$ws_endpoint_pt = "http://smarterfest-smarterservices.apps.softinsa.com/mobile/post_agenda_pt";
//$ws_endpoint_en = "http://smarterfest-smarterservices.apps.softinsa.com/mobile/post_agenda_en";

$ws_endpoint_pt = "https://smarterfest.eu-gb.mybluemix.net/mobile/post_agenda_pt";
$ws_endpoint_en = "https://smarterfest.eu-gb.mybluemix.net/mobile/post_agenda_en";



echo "PT result: " . export_json($servername, $username, $password, $dbname, "pt", $ws_username, $ws_password, $ws_endpoint_pt) . "</br>";
echo "EN result: " . export_json($servername, $username, $password, $dbname, "pt", $ws_username, $ws_password, $ws_endpoint_en);


function export_json($server, $user, $pass, $db, $lang, $ws_user, $ws_pass, $ws_endpoint) {


	// Create connection
	$conn = new mysqli($server, $user, $pass, $db);
	// Check connection
	if ($conn->connect_error) {
		die("Connection failed: " . $conn->connect_error);
	} 

	$all_ids = array(1 => '201, 203, 204'
						, '205, 207, 208'
						, '209, 211, 212'
						, '213, 215, 216'
						, '217, 219, 220'
						, '221, 223, 224'
						, '225, 227, 228'
						, '229, 231, 232'
						, '233, 235, 236'
						, '237, 239, 240');

	$final_json = array();
	foreach ($all_ids as $ids) {
		
		$sql = "SELECT texto_id, texto, texto_2lang FROM tabuleir_tabuleiros_db.festatabuleiros_texto WHERE texto_id in ($ids)";

		$result = $conn->query($sql);

		$date = "";
		$eventlist = "";
		
		$langfield = "texto";
		if ($lang != "pt"){
			$langfield = "texto_2lang";
		}
		
		if ($result->num_rows > 0) {
			// output data of each row
			while($row = $result->fetch_assoc()) {

				if ($date == ""){
					$date = str_replace("<p>", "", str_replace("</p>", "", $row["texto"]));
				}
				else{
					$eventlist = $eventlist . str_replace("<p>", "", $row[$langfield]);
				}
			}
			
			
			
			
			
			$meses_pt = array(1 => 'Março', 'Abril', 'Maio', 'Junho', 'Julho');
			$meses_en = array(1 => 'March', 'April', 'May', 'June', 'July');
			$meses_pt_abr = array(1 => 'Mar', 'Abr', 'Mai', 'Jun', 'Jul');
			$meses_en_abr = array(1 => 'Mar', 'Apr', 'May', 'Jun', 'Jul');
			$meses_num = array(1 => '-03', '-04', '-05', '-06', '-07');
			
			$eventos = explode("</p>", $eventlist);
			
			
			foreach ($eventos as $evento) {
				if ($evento !== "") {
					$init = 1;
					$end = 1;
					$month = "";
					if ($date == 'Abr-Jun') {
						$dt_part = explode("-", $date);
						if (is_numeric($dt_part[0])){
							$init = $dt_part[0];
							$dt_part[1] = str_replace("&nbsp;", " ", $dt_part[1]);
							$dt_part2 = explode(" ", $dt_part[1]);
							$end = $dt_part2[0];
							$month = $dt_part2[1];
						}
					} else {
						$dt_part2 = explode(" ", str_replace("&nbsp;", " ", $date));
						$init = $dt_part2[0];
						$end = $dt_part2[0];
						$month = $dt_part2[1];
					}
					for ($day = $init; $day <= $end; $day++) {

						$cols = explode("##", $evento);
						$date_final = $day . " " . $month;
						$start_hour = $cols[0];
						if (strpos($start_hour, '-') !== false) {
							$hrs = explode("-", $start_hour);
							$date_final = trim($hrs[0], " ");
							$start_hour = trim($hrs[1], " ");
						}
				
						for ($i = 1; $i <= 5; $i++) {
							$date_final = str_replace($meses_pt[$i], $meses_num[$i], $date_final);
							$date_final = str_replace($meses_en[$i], $meses_num[$i], $date_final);
							$date_final = str_replace($meses_pt_abr[$i], $meses_num[$i], $date_final);
							$date_final = str_replace($meses_en_abr[$i], $meses_num[$i], $date_final);
						}

						$date_final = date('Y-m-d', strtotime(str_replace("&nbsp;", "", str_replace(" ", "", $date_final)) . "-2019"));
						
						if (count($cols) == 5) {
							$coords = explode("*", $cols[4]);
							if (count($coords) == 2) {
								$arr = array('date' =>  $date_final
								   , 'start_hour' => html_entity_decode($start_hour)
								   , 'location' => str_replace("<strong>", "", str_replace("</strong>", "", str_replace("</a>", "", preg_replace("/<a href=.*?>/","",html_entity_decode($cols[1])))))
								   , 'latitude' => $coords[0]
								   , 'longitude' => $coords[1]
								   , 'description' => str_replace("<strong>", "", str_replace("</strong>", "", str_replace("</a>", "", preg_replace("/<a href=.*?>/","",html_entity_decode($cols[2])))))
								   , 'other_information' => ""
								   , 'download_link' => "");
							} else {
								$arr = array('date' =>  $date_final
									   , 'start_hour' => html_entity_decode($start_hour)
									   , 'location' => str_replace("</a>", "", preg_replace("/<a href=.*?>/","",html_entity_decode($cols[1])))
									   , 'description' => str_replace("</a>", "", preg_replace("/<a href=.*?>/","",html_entity_decode($cols[2])))
									   , 'other_information' => ""
									   , 'download_link' => "");
							}
							
						} else {
							$arr = array('date' =>  $date_final
								   , 'start_hour' => html_entity_decode($start_hour)
								   , 'location' => str_replace("</a>", "", preg_replace("/<a href=.*?>/","",html_entity_decode($cols[1])))
								   , 'description' => str_replace("</a>", "", preg_replace("/<a href=.*?>/","",html_entity_decode($cols[2])))
								   , 'other_information' => ""
								   , 'download_link' => "");
						}
						
								   
						array_push($final_json, $arr);
						
					}
				}
			}
			
		}
	}	

	$conn->close();
	
	$data_string = json_encode($final_json);  
	
	$ch = curl_init($ws_endpoint);                                                                      
	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST"); 
	curl_setopt($ch, CURLOPT_USERPWD, $ws_user . ":" . $ws_pass);                                                                    
	curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);                                                                  
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
	curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
		'Content-Type: application/json',
		'Accept: text/plain')                                                                       
	);                                                                                                                   
																														 
	$result = curl_exec($ch);
	return $result;
}
?> 