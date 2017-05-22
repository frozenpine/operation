ThinVNCApp = function(obj)
{
	var TVNCAPP = this;
	this.tv =  new ThinVNC();		
	var THIN = this.tv;	
	var toolbar;
	var pinned = 0;
	var clipbrdVisible = false;
	var dropVisible = false;
	
	
	this.tv.init(obj);
	
	$(window).bind('serverConnect', function(e){	
		
		$('#computer').unbind();
		$('#connect-page').hide();
		
		if(THIN.rcParams.id){
			document.body.style.backgroundColor = "#000";
		}
		
		if(document.getElementById('toolbar')==null){			
			$(document.body).prepend("<div id='toolbar' class='toolbar'><ul id='dropdown'><li><a href='#' id='ctrl-alt-del'>Ctrl+Alt+Del</a></li><li><a href='#' id='ctrl-esc'>Ctrl+Esc</a></li><li><a href='#' id='help-btn'>Help</a></li></ul><div id='toolbarHandle'></div><div id='mouse' class='btn icon mouse' title='Enables mouse and keyboard control.'>Control</div><div id='state'  class='btn icon pause' title='Pause'>pause</div><div id='refresh' class='btn icon refresh' title='Request a full display update.'>Refresh</div><div id='scale' class='btn icon scale' title='Scale the display to fit in the current window.'>Scale</div><div id='colors' class='btn icon colors' title='Changes color depth.'>Colors</div><div id='monitor' class='btn icon monitor' title='Next Monitor.'>Monitor</div><div id='clipbrd' class='btn icon clipbrd' title='Shows the clipboard window.'>Clipboard</div><div id='help' class='btn icon keyboard' title='Help'>Keyboard</div><div id='disconnect' class='btn icon disconnect' title='Scale the display to fit in the current window.'>Disconnect</div></div><div id='clipboard' class='commandline hidden'><div id='cliToolbar'><div id='clipbremcopy'  class='btn icon copy'  title='Copy the remote clipboard here'>Refresh</div><div id='clipbrempaste' class='btn icon paste' title='Paste the text below in the remote computer'>Paste</div><div id='clipblclclear' class='btn icon clear' title='Clear the text below'>Clear</div></div><div id='cliCmdLine'><textarea id='clipboardText' class='clipboardText' wrap='soft'></textarea></div></div><div id='help-content' title='Help'><p><strong>Keyboard shortcuts:</strong></p><ul><li><strong>CTRL+ALT+END</strong> (Open the Microsoft Windows NT Security dialog box)</li><li><strong>ALT+PAGE UP</strong> (Switch between programs from left to right)</li><li><strong>ALT+PAGE DOWN</strong> (Switch between programs from right to left)</li><li><strong>ALT+INSERT</strong> (Cycle through the programs in most recently used order)</li><li><strong>ALT+HOME</strong> (Display the Start menu)</li><li><strong>ALT+DELETE</strong> (Display the Windows menu)</li><li><strong>CTRL+ALT+Minus sign (-)</strong> (Place a snapshot of the entire client window area on the ThinVNC server clipboard and provide the same functionality as pressing ALT+PRINT SCREEN on a local computer.)</li><li><strong>CTRL+ALT+Plus sign (+)</strong> (Place a snapshot of the active window in the client on the ThinVNC server clipboard and provide the same functionality as pressing PRINT SCREEN on a local computer.)</li></ul></li></ul></div>");
			$('#monitor').addClass('hidden');	
			toolbar = document.getElementById('toolbar');
			toolbar.style.borderTop = "none";
			$('#help-content').dialog({ 
				autoOpen: false,
				draggable:true,
				width:600,
				height:300
			})
			startClipboard();
		}
		if(!THIN.iphone){
			$('#help').click(TVNCAPP.helpListener);	
			$('#help-btn').click(TVNCAPP.helpBtnListener);
			$('#ctrl-alt-del').click(TVNCAPP.ctrlAltDelListener);
			$('#ctrl-esc').click(TVNCAPP.ctrlEscListener);											
			$('#refresh').click(TVNCAPP.refreshListener);	
			$('#monitor').click(TVNCAPP.monitorListener);
			$('#scale').click(TVNCAPP.scaleListener);	
			$('#state').click(TVNCAPP.stateListener);	
			$('#colors').click(TVNCAPP.colorsListener);	
			$('#disconnect').click(TVNCAPP.disconnectListener);		
			$('#toolbarHandle').click(TVNCAPP.toolbarHandleListener);		
			$('#mouse').click(TVNCAPP.mouseListener);		
			$('#clipbrd').click(TVNCAPP.clipbrdListener);	
		}else{
			TVNCAPP.get("help").addEventListener("touchstart", TVNCAPP.helpListener, false);
			TVNCAPP.get("help-btn").addEventListener("touchstart", TVNCAPP.helpBtnListener, false);
			TVNCAPP.get("ctrl-alt-del").addEventListener("touchstart", TVNCAPP.ctrlAltDelListener, false);
			TVNCAPP.get("ctrl-esc").addEventListener("touchstart", TVNCAPP.ctrlEscListener, false);
			TVNCAPP.get("refresh").addEventListener("touchstart", TVNCAPP.refreshListener, false);
			TVNCAPP.get("monitor").addEventListener("touchstart", TVNCAPP.monitorListener, false);
			TVNCAPP.get("scale").addEventListener("touchstart", TVNCAPP.scaleListener, false);
			TVNCAPP.get("state").addEventListener("touchstart", TVNCAPP.stateListener, false);
			TVNCAPP.get("colors").addEventListener("touchstart", TVNCAPP.colorsListener, false);
			TVNCAPP.get("disconnect").addEventListener("touchstart", TVNCAPP.disconnectListener, false);
			TVNCAPP.get("toolbarHandle").addEventListener("touchstart", TVNCAPP.toolbarHandleListener, false);
			TVNCAPP.get("mouse").addEventListener("touchstart", TVNCAPP.mouseListener, false);
			TVNCAPP.get("clipbrd").addEventListener("touchstart", TVNCAPP.clipbrdListener, false);
		}
		$("#show-keyboard").hover(function(){
			this.style.backgroundColor = "#ADC5DA";
		},function(){
			this.style.backgroundColor = "#e4ecf3";
		});
		$("#show-keyboard").focus(TVNCAPP.showKeyboardListener);
	
		if(!$.browser.msie){
			$('#scale').addClass('pressed');
		}
	});
	this.get = function(id){
		return document.getElementById(id);	
	}
	this.helpListener = function(e){
		$('#dropdown').css('left', $('#help').position().left);					
				
		if(dropVisible){
			$('#dropdown').hide();
			$(this).removeClass('pressed');
			dropVisible = false;
		}else{ 
			$('#dropdown').show();
			$(this).addClass('pressed');
			dropVisible = true;
		}			
	}
	this.helpBtnListener = function(e){
		$('#dropdown').hide();
		dropVisible = false;
		$('#help').removeClass('pressed');
		
		if($('#help-content').dialog('isOpen')){
			$('#help-content').dialog('close');
		}else{ 
			$('#help-content').dialog('open');			
		}		
	}

	this.ctrlAltDelListener = function(e){
		$('#dropdown').hide();
		dropVisible = false;
		$('#help').removeClass('pressed');
		
		THIN.sendFunctionKey("CtrlAltDel");		
	}
	this.ctrlEscListener = function(e){
			
		$('#dropdown').hide();
		dropVisible = false;
		$('#help').removeClass('pressed');

		THIN.sendFunctionKey("CtrlEsc");		
	}
	this.showKeyboardListener = function(e){			
		$('#help').removeClass('pressed');
		$('#dropdown').hide();
		var sk = document.getElementById('show-keyboard');
		dropVisible = false;		
		e.stopPropagation();
	}	
	this.refreshListener = function(e){
		if(THIN.rcParams.active){ 
			THIN.refresh();
		}		
	}
	this.monitorListener = function(e){
		THIN.setMonitor(THIN.rcParams.monitor+1);		
	}
	this.scaleListener = function(e){
		if(!$.browser.msie){
			THIN.rcParams.scaled = !THIN.rcParams.scaled;
			
			if(!THIN.rcParams.scaled){
				document.body.style.overflow = "auto";	
			}else{
				document.body.style.overflow = "hidden";	
			}
			THIN.zoomDesktop();
			if (THIN.rcParams.scaled) $('#scale').addClass('pressed');
			else $('#scale').removeClass('pressed');					
		}		
	}
	this.stateListener = function(e){
		if (THIN.rcParams.active){ 			
			THIN.stop();
		}else{
			THIN.start();
		}		
	}
	this.colorsListener = function(e){
		THIN.swicthPixelFormat();
	}
	this.disconnectListener = function(e){
		THIN.disconnect();
	}
	this.toolbarHandleListener = function(e){
		THIN.pinned = THIN.pinned ^ 1;
		if (THIN.toolbar.offsetTop < 0) {
			THIN.showToolbar();
		} else {
			THIN.hideToolbar();
		}		
	}
	this.mouseListener = function(e){
		THIN.toogleMouseControl();
	}
	this.clipbrdListener = function(e){
		if(THIN.rcParams.mouseControl){
			e.stopPropagation();
			if (clipbrdVisible == true) {
				clipbrdVisible = false;
				$('#clipbrd').removeClass('pressed');
				$('#clipboard').addClass('hidden');
			} else {
				clipbrdVisible = true;
				$('#clipbrd').addClass('pressed');
				$('#clipboard').css('top', $('#clipbrd').offset().top + 22);
				$('#clipboard').css('left', $('#clipbrd').offset().left);

				$('#clipbremcopy').click();
				$('#clipboard').removeClass('hidden');
			}
		}		
	}

	THIN.sendParams = function(mouseControl,remotePointer,pixelFormat){		
			THIN.sendCmd("cmd=params&mouseControl=" + mouseControl + "&kbdControl=" + mouseControl + "&remotePointer=" + remotePointer+ "&pixelFormat=" + pixelFormat);
	}
	
	THIN.toogleMouseControl = function() {
		THIN.sendParams(!THIN.rcParams.mouseControl,THIN.rcParams.remotePointer,THIN.rcParams.pixelFormat);
	}

	
	THIN.toogleRemotePointer = function() {
		THIN.sendParams(THIN.rcParams.mouseControl, !THIN.rcParams.remotePointer,THIN.rcParams.pixelFormat);
	}

	
	THIN.swicthPixelFormat = function() {
		var pf = 0;
		if (THIN.rcParams.pixelFormat==0) pf = 1;
		THIN.sendParams(THIN.rcParams.mouseControl, THIN.rcParams.remotePointer,pf);
	}		
	$(window).bind('serverDisconnect', function(){
		document.body.style.backgroundColor = "#FFF";				
		if(clipbrdVisible){	
			$('#clipbrd').removeClass('pressed');
			$('#clipboard').addClass('hidden');		
		}		
		TVNCAPP.dispose();	
//		$('#desk').hide();
//		$('#connect-page').show();
		
	});
	$(window).bind('serverReconnect', function(){
		$('#help-btn').unbind();
		$('#ctrl-esc').unbind();
		$('#ctrl-alt-del').unbind();
		$('#help').unbind();
		$('#cursor').unbind();
		$('#refresh').unbind();
		$('#monitor').unbind();
		$('#scale').unbind();
		$('#state').unbind();
		$('#colors').unbind();
		$('#disconnect').unbind();
		$('#toolbarHandle').unbind();
		$('#mouse').unbind();
		$('#clipbrd').unbind();

		if(clipbrdVisible){	
			$('#clipbrd').removeClass('pressed');
			$('#clipboard').addClass('hidden');		
		}	
	});
	
	this.dispose = function (){		
		$(window).unbind();
		if(document.getElementById('toolbar')!=null){
			$('#help-btn').unbind();
			$('#ctrl-esc').unbind();
			$('#ctrl-alt-del').unbind();			
			$('#cursor').unbind();
			$('#refresh').unbind();
			$('#monitor').unbind();
			$('#scale').unbind();
			$('#state').unbind();
			$('#colors').unbind();
			$('#disconnect').unbind();
			$('#toolbarHandle').unbind();
			$('#mouse').unbind();
			$('#clipbrd').unbind();
			$('#toolbar').remove();
			$('#help-content').remove();			
		}
		
		delete TVNCAPP;
		delete THIN;
		
		delete THIN.tv;
		delete this;

	}	
	$(window).resize(function(){			
			THIN.resetToolbarPosition();
		
	});
	$(window).bind("onServerCommandResult", function(e, obj) {  					
					if( THIN.connected){
						if (THIN.rcParams.active) {
							document.getElementById("state").textContent = "pause";
							$('#state').removeClass('resume').addClass('pause');
						} else {
							document.getElementById("state").textContent = "resume";
							$('#state').removeClass('pause').addClass('resume');
						}
												
						if (obj.ticket!='') {
							$('#mouse').addClass('hidden');
							$('#monitor').addClass('hidden');
							$('#cursor').addClass('hidden');
							$('#state').addClass('hidden');
							$('#clipbrd').addClass('hidden');
							$('#help').addClass('hidden');
						} else {
							if (THIN.rcParams.active && THIN.rcParams.mouseControl) {
								$('#mouse').addClass('pressed');
							} else $('#mouse').removeClass('pressed');
			
							if (THIN.rcParams.active && THIN.rcParams.remotePointer) {
								$('#cursor').addClass('pressed');
							} else $('#cursor').removeClass('pressed');
			
							if (THIN.rcParams.monitorCount>1) {
								$('#monitor').removeClass('hidden');
							}
						}
			
						if (THIN.rcParams.pixelFormat==1) {
							document.getElementById("colors").textContent = 'FULL COLOR';
						} else {
							document.getElementById("colors").textContent = '256 COLOR';
						}
						THIN.resetToolbarPosition();
					}

	});  	
	THIN.resetToolbarPosition = function (){
		var ww = window.innerWidth;
		if(THIN.toolbar = document.getElementById('toolbar')){			
			THIN.toolbar.style.left = ((ww - THIN.toolbar.offsetWidth) / 2)+'px';				
			var toolbarHandle = document.getElementById('toolbarHandle');
			toolbarHandle.style.top = (THIN.toolbar.offsetHeight - 1)+'px';
			toolbarHandle.style.left = (THIN.toolbar.offsetWidth - 19) + 'px';	
			//toolbarHandle.style.zIndex = 9000000;			
			THIN.toolbar.style.visibility = "visible";
			toolbarHandle.style.visibility = "visible";
		}
	};

	THIN.hideToolbar = function() {
		THIN.toolbar.style.top = - THIN.toolbar.offsetHeight + 'px';
		THIN.resetToolbarPosition();
	}
	
	THIN.showToolbar = function() {
		THIN.toolbar.style.top = 0 + 'px';
		THIN.resetToolbarPosition();
	}
	
	function CommandLineInterface() {
		var type = "unknown";
		var div = null;
	
		this.init = cliInit;
		this.dispose = cliDispose;
		this.show = cliShow;
		this.hide = cliHide;
		this.getText = cliGetText;
		this.setText = cliSetText;
		this.send = cliSend;
		this.recv = cliReceive;
	}
	
	function cliInit(element) {
		this.div = element;
		if (this.div == null || this.div == undefined) {
			throw "Element with Id = '" + id + "' not found in the DOM";
		}
	}
	
	function cliDispose() {
		this.div = null;
	}
	
	function cliShow() {
		div.style.display = 'inline';
	}
	
	function cliHide() {
		div.style.display = 'none';
	}
	
	function cliGetText() {
		return this.div.innerText;
	}
	
	function cliSetText(text) {
		this.div.innerText = text;
	}
	
	function cliSend(action) {
		var url = THIN.baseUrl + "cmd?id=" + THIN.rcParams.id + "&cmd=cli&type=" + this.type + "&action=" + action;
		var txt = this.getText();
		try{
			if(THIN.rcParams.mouseControl){	
				$.post(url, txt, fn = function(obj) {
					delete fn;
				});
			}
		}
		catch (e) {
			alert(e);
		}
	}
	
	function cliReceive(action) {
		var url = THIN.baseUrl + "cmd?id=" + THIN.rcParams.id + "&cmd=cli&type=" + this.type + "&action=" + action;
		var me = this;
		try {
			$.getJSON(url, fn = function(obj) {
				delete fn;
				me.setText(obj.text);
				me = null;
			});
		}
		catch (e) {
			alert(e);
		}
	}
	
	
	/* Clipboard */
	
	function CLI4Clipboard() {
		this.inheritFrom = CommandLineInterface;
		this.inheritFrom();
		this.type = "clipboard";
	
		this.getText = clipboardGetText;
		this.setText = clipboardSetText;
		this.copy = clipboardCopy;
		this.paste = clipboardPaste;
		this.clear = clipboardClear;
	}
	
	function clipboardGetText() {
		return $('textarea#clipboardText').val();
	}
	
	function clipboardSetText(text) {
		$('textarea#clipboardText').val(text);
	}
	
	function clipboardCopy() {
		this.recv("copy");
	}
	
	function clipboardPaste() {
		this.send("paste");
	}
	
	function clipboardClear() {
		$('textarea#clipboardText').val("");
	}
	
	/* Startup functions */
	function startClipboard() {
		jQuery.ajaxSettings.contentType = 'text/plain';
		var clipboard = new CLI4Clipboard();
		clipboard.init($('#clipboard'));
		$('#clipbremcopy').click(function() {		
			clipboard.copy();
		});
		$('#clipbrempaste').click(function() {
			clipboard.paste();
		});
		$('#clipblclclear').click(function() {
			clipboard.clear();
		});
		$('#clipboardText').keydown(function (e) {
			e.stopPropagation();
		});
		$('#clipboardText').keyup(function (e) {
			e.stopPropagation();
		});
		$('#clipboardText').focus(function (e) {
			THIN.removeListeners();
		});	
		$('#clipboardText').blur(function (e) {
			THIN.hookKM();	
		});				
	}	
	
	
	
}

