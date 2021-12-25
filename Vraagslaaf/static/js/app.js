define(['jquery', 'rngModule', 'reelModule', 'uiModule', 'audioModule'], function($, rngModule, reelModule, uiModule, audioModule) {
	var initialize = function() {
		// Initialize modules
		rngModule.rngmoduleinitialize();
		reelModule.reelmoduleinitialize();
		uiModule.uimoduleinitialize();
		audioModule.audiomoduleinitialize();
		// audioModule.audiomoduleplayaudio('themeSong');
		// audioModule.audiomoduleplayaudio('casinoAmbience');
    $('#reel-buttons').hide()
   
	};

  var test = function() {
    console.log("this gets called")
	var targetContainer = document.getElementById("spinning-user");
    var eventSource = new EventSource("/stream");
    eventSource.onmessage = function(e) {
      if (!reelModule.reelmoduleisspinning()){
          console.log(e)
          d = JSON.parse(e.data)
          console.log(d)
          console.log(d.rolls)
          targetContainer.innerHTML = "We rollen nu voor: " + d.name;
          nmbrs = reelModule.reelmodulespin(d.rolls);
        } 
    };
   
	};

  

	return {
		initialize: initialize,
    test: test
	};
});


