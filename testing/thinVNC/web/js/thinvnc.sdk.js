ThinVNC = function(){
	var TVNC = this;
	
/*
	if(typeof console == "undefined"){
		var console = {
			log:function(){
				//log function	
			}
		}
	}	
*/	
	this.mouseX = -1;
	this.mouseY = -1;
	this.mouseMoved = false;
	this.vncdiv;
	this.vncDivElement;
	this.baseZIndex = 800000;
	this.iphone;
	this.supportsCanvas;
	this.scale = 1;
	this.startPending = true;
	this.jsonTimeoutValue = 60000;
	this.jsonTimeout;
	this.disposeTimeoutValue = 1000;
	this.disposeTimeout;
	this.vncdivId = "mainPanel";
	this.reconnectDivId = "recnx";
	this.cursorCanvas = null;

	this.queueRequestName = 'requestQueue';
	this.reconnectDelay = 0;
	this.connected = null;
	this.baseUrl = '';
	this.useAjax = true;
	this.ws = null;
	this.alive = null;
	this.connecting = false;
	this.xmlHttpJson = null; 
	this.lastKeyCode = 0;
	this.reconnecting = false;
	this.touching = false;
		
	this.rcParams = {
		id: 0,
		active: false,
		monitor: 0,
		monitorCount: 0,
		viewLeft: 0,
		viewTop: 0,
		viewWidth: 0,
		viewHeight: 0,
		mouseControl: true,
		kbdControl: true,
		quality: 90,
		pixelFormat: 0,
		grayscale: false,
		imageMethod : 2,
		remotePointer: true,
		scaled: true, 
		interactive:true,
		divId:null,
		url:null,
		reconnectDelay: 3000,
		address: "",
		ticket:""
	}

	this.getBodyHeight = function(){
		return this.vncDivElement.parent().height();
	}
	
	this.getBodyWidth = function(){
		return  TVNC.vncDivElement.parent().width();
	}
	this.findPos = function(obj) {
		var curleft = 0;
		var curtop = 0;
			
		do {
			
			if(obj.id == this.vncdivId && !jQuery.browser.mozilla && !jQuery.browser.opera && !jQuery.browser.webkit){				
				curleft += obj.offsetLeft * TVNC.scale;
				curtop += obj.offsetTop * TVNC.scale;					
			}else{
				curleft += obj.offsetLeft;
				curtop += obj.offsetTop;		
			}

		} while (obj = obj.offsetParent);
		return [curleft,curtop];
	}
	this.serverMouseX = function(e){						
		var position = this.findPos(TVNC.vncdiv);		
		var left =  position[0];												
		if(TVNC.iphone)	return Math.floor((e.touches[0].pageX - left) / TVNC.scale);
		else			return Math.floor((e.pageX - left) / TVNC.scale);	
	}

	this.serverMouseY = function(e){
		var position = this.findPos(TVNC.vncdiv);		
		var top = position[1];	
		if(TVNC.iphone)	return Math.floor((e.touches[0].pageY - top) / TVNC.scale);	
		else			return Math.floor((e.pageY - top) / TVNC.scale);	
	}
	this.center = function(){
		var s = (jQuery.browser.mozilla || jQuery.browser.opera || jQuery.browser.webkit)? TVNC.getScale() : 1;
	
		var ml = (TVNC.vncdiv.offsetWidth * s)/2;
		var mt = (TVNC.vncdiv.offsetHeight * s)/2;


		
		if(this.rcParams.scaled 
			|| TVNC.getBodyHeight() > TVNC.vncdiv.offsetHeight 
			&& TVNC.getBodyWidth() > TVNC.vncdiv.offsetWidth){
			
			TVNC.vncdiv.style.top = '50%';
			TVNC.vncdiv.style.marginTop = -mt + 'px';
			TVNC.vncdiv.style.left = '50%';
			TVNC.vncdiv.style.marginLeft = -ml + 'px';		
				
		}else{
			
			if(TVNC.getBodyHeight() > TVNC.vncdiv.offsetHeight) {
				TVNC.vncdiv.style.top = '50%';
				TVNC.vncdiv.style.marginTop = -mt + 'px';		
				TVNC.vncdiv.style.left = '0px';
				TVNC.vncdiv.style.marginLeft = '0px';				
			}else if( TVNC.getBodyWidth() > TVNC.vncdiv.offsetWidth){
				TVNC.vncdiv.style.left = '50%';
				TVNC.vncdiv.style.marginLeft = -ml + 'px';					
				TVNC.vncdiv.style.top = '0px';
				TVNC.vncdiv.style.marginTop = '0px';						
			}else{			
				TVNC.vncdiv.style.top = '0px';
				TVNC.vncdiv.style.marginTop = '0px';
				TVNC.vncdiv.style.left = '0px';
				TVNC.vncdiv.style.marginLeft = '0px';						
			}					
		}		
	}
	
	this.setScaled = function(value){
		this.rcParams.scaled = value;
	}
	
	this.getScale = function(){
		if (!TVNC.rcParams.scaled)return 1;
		
		var c1 = TVNC.getBodyHeight() / TVNC.rcParams.viewHeight;
		var c2 = TVNC.getBodyWidth() / TVNC.rcParams.viewWidth;
		
		if ((c1 > 1) && (c2 > 1)) 
			return 1;
		else {
			if (c2 < c1) 
				return c2;
			else 
				return c1;
		}
	}
	
	this.moveCursorCanvas = function(x,y)
	{
		if (TVNC.cursorCanvas) {
			var position = TVNC.findPos(TVNC.vncdiv);
			var cX =  Math.floor((x - position[0]) / TVNC.scale) - TVNC.cursorCanvas.hotspotX;	
			var cY =  Math.floor((y - position[1]) / TVNC.scale) - TVNC.cursorCanvas.hotspotY;	
			TVNC.cursorCanvas.style.left = cX + 'px';
			TVNC.cursorCanvas.style.top = cY + 'px';
		}			
	}

	this.zoomDesktop = function(){
		this.scale = TVNC.getScale();
		this.center();
		
		if ($.browser.mozilla) {
			this.vncdiv.style.MozTransformOrigin = "top left";
			this.vncdiv.style.MozTransform = "scale(" + this.scale + ")";
		}
		if ($.browser.opera) {
			this.vncdiv.style.OTransformOrigin = "top left";
			this.vncdiv.style.OTransform = "scale(" + this.scale + ")";
		}
		if ($.browser.webkit) {
			this.vncdiv.style.WebkitTransformOrigin = "top left";
			this.vncdiv.style.WebkitTransform = "scale(" + this.scale + ")";
		}
		if ($.browser.msie) {
		//this.vncdiv.style.zoom = this.scale;			
		}
	}
	
	this.createCanvas = function(win){
		var canvas = document.createElement("canvas");		
		canvas.visibility = 'visible';
		canvas.display = 'block';
		canvas.style.position = 'absolute';
		canvas.style.left = (win.left - TVNC.rcParams.viewLeft) + 'px';
		canvas.style.top = (win.top - TVNC.rcParams.viewTop) + 'px';		
		canvas.style.zIndex = this.baseZIndex + win.zidx;
		canvas.width = win.width; 
		canvas.height = win.height;
		canvas.id = "canvas" + win.hwnd;
		canvas.mask = new Object();
		canvas.mask.color = '#000';
		canvas.mask.visible = false;
		this.vncdiv.appendChild(canvas);
		return canvas;
	}
	
	this.processWindow = function(win){
		
		var canvasid = "canvas" + win.hwnd;
		var canvas = document.getElementById(canvasid);
		if (!canvas) {
			canvas = this.createCanvas(win);
		}
		
		if (win.hwnd == 0) {
			this.cursorCanvas = canvas;
			canvas.hotspotX = win.dx;
			canvas.hotspotY = win.dy;
			canvas.style.zIndex = this.baseZIndex + 5000;
		}

		if ((win.width == 0) || (win.height == 0)) {
			canvas.style.visibility = "hidden";
			canvas.style.zIndex = -1;
		}
		else {			
			if (this.cursorCanvas != canvas) {
				canvas.style.left = (win.left - TVNC.rcParams.viewLeft) + 'px';
				canvas.style.top = (win.top - TVNC.rcParams.viewTop) + 'px';
			}
			if ((win.width != canvas.width) || (win.height != canvas.height)) {
				if (canvas.width * canvas.height == 0) {
					canvas.width = win.width;
					canvas.height = win.height;
					
				} else {
					var context = canvas.getContext('2d');
				
					if ($.browser.mozilla) {
						var dataURL = canvas.toDataURL("image/png");
						var img = new Image();
						var savedWidth = canvas.width;
						var savedHeight = canvas.Height;
						img.onload = function(){
							context.drawImage(img, 0, 0);
						}
						img.src = dataURL;
						canvas.width = win.width;
						canvas.height = win.height;
					}
					else {
						var imagedata = context.getImageData(0, 0, canvas.width, canvas.height);
						canvas.width = win.width;
						canvas.height = win.height;
						context.putImageData(imagedata, 0, 0);
					}
					context.strokeRect(0, 0, canvas.width, canvas.height);
				}
			}
//			canvas.style.clip = 'rect(0px,' + win.width + 'px,' + win.height + 'px,0px)';			
			canvas.style.visibility = "visible";
			canvas.style.zIndex = this.baseZIndex + win.zidx;
		}
		
		if (!canvas.mask.visible && win.mask) {
			var context = canvas.getContext('2d');
			context.fillStyle = canvas.mask.color;
			context.fillRect(0, 0, canvas.width, canvas.height);
		}
		canvas.mask.visible = win.mask;
		
		if (win.imgs != null) {
			var context = canvas.getContext('2d');
			if (!context || !context.drawImage) {
				alert("there is no canvas");
				return;
			};
			
			if (this.cursorCanvas == canvas) {
				context.clearRect(0, 0, win.width, win.height);
			};
			
			$.each(win.imgs, function(i, imgpart){
				var img = new Image();
				img.id = "imgcanvas";
				img.style.display = "none";
				img.onload = function(){
					context.drawImage(img, imgpart.x, imgpart.y, img.width, img.height);
				}
				img.src = imgpart.img;
			})


		}
	};
	
	this.sendServerCmd = function(cmd, query){			
		if(TVNC.connected){
			var url = TVNC.baseUrl + cmd + "?" + query + "&id=" +  this.rcParams.id;		
			if (this.useAjax){ 		
				$.ajaxq(this.queueRequestName,{
				  url: url,
				  success: TVNC.serverCmdResult
				});
			}else{ 
				this.ws.send(query + "&id=" + this.rcParams.id);		
			}
		}
	}

	this.receiveScreen = function(obj){			
		TVNC.scale = TVNC.getScale();
		try {
			if ((obj == undefined) || (obj == null) || (obj.status == 2)) {
				setTimeout(TVNC.reload, 1);
				return;
			}
			
			if (obj.status == 9) {
				alert("This session has been terminated");
				TVNC.disconnect();
				return;
			}
			
			$.each(obj.windows, function(i, win){
				TVNC.processWindow(win);
			})
			
			for (var i = TVNC.vncdiv.children.length - 1; i >= 0; i--) {
				var found = false;
				var canvas = TVNC.vncdiv.children[i];
				
				$.each(obj.windows, function(i, win){
					var canvasid = "canvas" + win.hwnd;
					if (canvas.id == canvasid) {
						found = true;
					}
				})
				if (!found) {
					canvas.style.display = "none";
					canvas.innerHTML = '';
					TVNC.vncdiv.removeChild(canvas);
				}
			}
			if (!TVNC.rcParams.remotePointer && !TVNC.rcParams.mouseControl) {
				TVNC.vncdiv.style.cursor = 'default';
			}
			
			if (TVNC.rcParams.mouseControl && !TVNC.rcParams.remotePointer) {
				TVNC.vncdiv.style.cursor = obj.cursor;
			}

			TVNC.zoomDesktop(true);					
			
			if (obj.status == 3) 
				setTimeout(TVNC.reconnect, 1);
			else 
				if (TVNC.rcParams.active) 
					setTimeout(TVNC.reload, 1);
			
		} 
		catch (err) {
			if (TVNC.rcParams.active) {
				setTimeout(TVNC.reload, 1);
			}
		}
	}
	
	this.serverCmdResult = function(data){						
			
				var obj = null;			
				
				if(TVNC.useAjax){
					obj = eval('(' + data + ')');
				}else{
					obj = data;
				}
				if (!obj.id){
					return;	
				}
				if (obj.id == '##') {
					TVNC.dispose();
					return;
				}
				if (TVNC.rcParams.active != obj.active) {
					if (obj.active) {
						TVNC.reload();
					}
				}		

				TVNC.rcParams.active = obj.active;
				TVNC.rcParams.monitor = obj.monitor;
				TVNC.rcParams.monitorCount = obj.monitorCount;
				TVNC.rcParams.viewLeft = obj.viewLeft;
				TVNC.rcParams.viewTop = obj.viewTop;
				TVNC.rcParams.viewWidth = obj.viewWidth;
				TVNC.rcParams.viewHeight = obj.viewHeight;
				TVNC.rcParams.mouseControl = obj.mouseControl;
				TVNC.rcParams.kbdControl = obj.kbdControl;
				TVNC.rcParams.quality = obj.quality;
				TVNC.rcParams.pixelFormat = obj.pixelFormat;
				TVNC.rcParams.grayscale = obj.grayscale;
				TVNC.rcParams.remotePointer = obj.remotePointer;
				TVNC.rcParams.imageMethod = obj.imageMethod;
				
				if (TVNC.rcParams.remotePointer) {				
					var bw = navigator.userAgent;			
					if (bw.indexOf('Chrome')== -1) {
						TVNC.vncdiv.style.cursor = 'url("images/blank.cur"),url("/images/blank.cur"),default'
					} else {
						TVNC.vncdiv.style.cursor = 'url("images/point.cur"),url("/images/point.cur"),default'
					}
				}
						
				TVNC.vncdiv.style.width = TVNC.rcParams.viewWidth + 'px';				
				TVNC.vncdiv.style.height = TVNC.rcParams.viewHeight + 'px';
				TVNC.vncdiv.style.clip = 'rect(0px,' + TVNC.rcParams.viewWidth + 'px,' + TVNC.rcParams.viewHeight + 'px,0px)';
		
				if (TVNC.rcParams.active && TVNC.rcParams.mouseControl) {
					setTimeout(TVNC.sendMouseMove, 100);
				};
				
				if (TVNC.startPending) 
					setTimeout(TVNC.start, 1);
					
				$(window).trigger("onServerCommandResult", obj);
		
	}
	
	this.sendCmd = function(query){				
		return this.sendServerCmd("cmd", query);
	}
	

	this.setMouseControl = function(value) {
		this.sendCmd("cmd=params&mouseControl=" + value + "&kbdControl=" + !TVNC.rcParams.kbdControl);
	}

	this.setQuality = function(value) {
		this.sendCmd("cmd=params&quality=" + value);
	}

	this.setimageMethod = function(value) {
		this.sendCmd("cmd=params&imageMethod=" + value);
	}
	
	this.setGrayscale = function(value) {
		this.sendCmd("cmd=params&grayscale=" + value);
	}

	this.setKbdControl = function(value) {
		this.sendCmd("cmd=params&kbdControl=" + value);
	}

	this.setRemotePointer = function(value) {
		this.sendCmd("cmd=params&remotePointer=" + value);
	}

	this.setPixelFormat = function(value){
		this.sendCmd("cmd=params&pixelFormat=" + value);
	}
	
	this.setMonitor = function(m){
		if (m >= this.rcParams.monitorCount) 
			m = -1;
		this.sendCmd("cmd=params&monitor=" + m);
	}
	
	this.clearSID = function(){
		var d = new Date();
		document.cookie = "SID=; expires=-1;";	
	}	
	this.disconnect = function(){
		if(document.getElementById(TVNC.reconnectDivId)){
			$('#'+TVNC.reconnectDivId).remove();		
		}		
		TVNC.disposeTimeout = setTimeout(TVNC.dispose, TVNC.disposeTimeoutValue);		
		TVNC.sendCmd("cmd=disconnect");
	}
	this.removeListeners = function(){
		$(document).unbind();
		$('#'+TVNC.vncdivId).unbind();
		window.removeEventListener('DOMMouseScroll',  TVNC.wheel, false);	
		window.onmousewheel = null;
	}
	this.dispose = function(){
		TVNC.alive = false;		
		clearTimeout(TVNC.disposeTimeout);
		if (!TVNC.useAjax) {
			TVNC.ws.close();
		}
		TVNC.connected = false;
		TVNC.connecting = false;
		TVNC.useAjax = true;
		
		TVNC.removeListeners();
		$(window).trigger("serverDisconnect");
		$(window).unbind();
		TVNC.clearSID();
		TVNC.vncdiv.innerHTML = '';
		if(TVNC.xmlHttpJson){
			TVNC.xmlHttpJson.abort();					
			TVNC.xmlHttpJson = null;		
		}
		
	}
	this.stop = function(){
		this.sendCmd("cmd=stop");
	}
	
	this.start = function(){
		this.startPending = false;
		this.rcParams.active = false;
		var cmd = "cmd=start"
		cmd = cmd + "&mouseControl=" + this.rcParams.mouseControl + "&kbdControl=" + this.rcParams.kbdControl;
		cmd = cmd + "&quality=" + this.rcParams.quality + "&pixelFormat=" + this.rcParams.pixelFormat;
		cmd = cmd + "&monitor=" + this.rcParams.monitor;
		TVNC.sendCmd(cmd);
		$('#'+TVNC.vncdivId).show();
	}
	this.connect = function(){		
		if(!this.connecting && !this.connected && TVNC.xmlHttpJson == null){
			this.clearSID();			
			var cmd = 'cmd';
			var query = "cmd=connect";
			
			if( TVNC.rcParams.ticket !== ''){
				query = query + "&ticket=" + TVNC.rcParams.ticket;
			}
			query = query + "&destAddr=" + TVNC.rcParams.address;			
			
			var url = TVNC.baseUrl + cmd + "?" + query + "&id=" +  TVNC.rcParams.id;		
			this.connecting = true;
			TVNC.xmlHttpJson = $.ajax({
			  url: url,	
			  error:function(){
				TVNC.connecting = false;
				TVNC.xmlHttpJson = null;
			  },
			  success: TVNC.onConnectResult
			});
			$(window).trigger("serverConnecting");						
		}
	}
	this.onConnectResult = function(data){
		TVNC.xmlHttpJson = null;
		TVNC.connecting = false;	
		
		if(data != "" && data){
			try {
				var obj = eval('(' + data + ')');
				if(obj.status && obj.status != undefined ){								
					TVNC.connected = true;
					TVNC.reconnecting = false;
					TVNC.rcParams.id = obj.id;
					TVNC.vncdiv.innerHTML = '';
					if("WebSocket" in window){ 										
						TVNC.connectWebSocket(); // try websockets transfer
					}else{
						TVNC.start(); // websockets isn't available, try ajax transfer
					}				
					TVNC.hookKM();				
					$(window).trigger("serverConnect", obj);				
				}else if(obj.errormsg){
					if(!TVNC.reconnecting){
						alert('connection failed');	
						$(window).trigger("serverConnectionError");
						TVNC.dispose();
					}else{
						TVNC.reconnect();	
					}
				}
			} catch(err) {
				TVNC.reconnect();
			}
		}else{
			TVNC.reconnect();
		}
	}
	this.gup = function( name )
	{
	  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
	  var regexS = "[\\?&]"+name+"=([^&#]*)";
	  var regex = new RegExp( regexS );
	  var results = regex.exec( window.location.href );
	  if( results == null )
		return "";
	  else
		return results[1];
	}	
	this.refresh = function(){
		this.vncdiv.innerHTML = '';
		this.sendCmd("cmd=refresh");
	}
	
	this.onJsonTimeout = function(){
		if(TVNC.xmlHttpJson)
			TVNC.xmlHttpJson.abort();					


		TVNC.xmlHttpJson = null;	
		TVNC.reconnect();			
	}
	
	this.reload = function(){
		if(!TVNC.connected) return;
		
		if (TVNC.useAjax) {
			var url = TVNC.baseUrl + "json?id=" + TVNC.rcParams.id;
			clearTimeout(TVNC.jsonTimeout);
			TVNC.jsonTimeout = setTimeout(TVNC.onJsonTimeout, TVNC.jsonTimeoutValue);
			
			if(TVNC.xmlHttpJson == null){
				TVNC.xmlHttpJson = $.ajax({
				  url: url,			  
				  error:function(){
 					TVNC.reconnect();
					TVNC.xmlHttpJson = null;
				  },
				  success: function(data){					
					if(TVNC.connected){
						if(data != "" && data){
							try {
								var obj = eval('(' + data + ')');
								TVNC.receiveScreen(obj);
								TVNC.xmlHttpJson = null;
							} catch(err) {
								TVNC.xmlHttpJson = null;
								TVNC.reconnect();
							}
						}else{
							TVNC.xmlHttpJson = null;
							TVNC.reconnect();
						}
					}
				  }
				});
			}
		}
		else {
			TVNC.ws.send('cmd=ready');
		}				
	}
	
	this.clearMouse = function(){
		this.mouseMoved = false;
	}
	this.sendEvent = function(url){		
		$.ajaxq(this.queueRequestName,{url:url,async:true});
	}
	
	this.sendKey = function(key,char, action){
		if (TVNC.rcParams.active && TVNC.rcParams.kbdControl) {
			var query = "cmd=keyb&key=" + key + "&char="+ char +"&action=" + action + "&id=" + TVNC.rcParams.id;
			if (TVNC.useAjax) {
				var url = TVNC.baseUrl + "cmd?"+query;
		        this.sendEvent(url);
			} else TVNC.ws.send(query);							
		}
	}
	
	this.sendFunctionKey = function(key){
		if (TVNC.rcParams.active && TVNC.rcParams.kbdControl) {
			var query = "cmd=fkey&key=" + key + "&id=" + TVNC.rcParams.id;
			if (TVNC.useAjax) {
				var url = TVNC.baseUrl + "cmd?"+query;
		        this.sendEvent(url);
			} else TVNC.ws.send(query);							
		}
	}

	this.sendMouse = function(x, y, button, action){
		if (TVNC.rcParams.active && TVNC.rcParams.mouseControl) {
			TVNC.clearMouse();	
				
				x = x + TVNC.rcParams.viewLeft;
				y = y + TVNC.rcParams.viewTop;
				var query = "cmd=mouse&x=" + x + "&y=" + y + "&btn=" + button + "&action=" + action + "&id=" + TVNC.rcParams.id;
				if (TVNC.useAjax) {
					var url = TVNC.baseUrl + "cmd?"+query;
					TVNC.sendEvent(url);
				} else TVNC.ws.send(query);							
				
		}
	}
	
	this.sendMouseMove = function(){
		if (TVNC.rcParams.active && TVNC.rcParams.mouseControl) {
			if (TVNC.mouseMoved) {
				TVNC.sendMouse(TVNC.mouseX, TVNC.mouseY, 0, "move");
			}
			setTimeout(TVNC.sendMouseMove, 100);
		}
	}
	this.sendWheel = function(delta){
		if (TVNC.rcParams.active && TVNC.rcParams.mouseControl) {
				var query = "cmd=mouse&action=wheel&delta=" + delta + "&id=" + TVNC.rcParams.id;
				
				if (TVNC.useAjax) {
					var url = TVNC.baseUrl + "cmd?"+query;
					TVNC.sendEvent(url);
				} else TVNC.ws.send(query);							
				
		}				
	}
	this.wheel = function(event){
			var delta = 0;
			if (!event) event = window.event;
			if (event.wheelDelta) {
					delta = event.wheelDelta; 
					if (jQuery.browser.opera) delta = -delta;
			} else if (event.detail) {
					delta = -event.detail*120;///3;
			}
			if (delta) TVNC.sendWheel(delta);
			event.stopPropagation();
			event.preventDefault();
	}

	this.IsFunctionKey = function(keyCode){
		return ((keyCode>=112) && (keyCode<=123) ||
			(keyCode>=33) && (keyCode<=40) ||
			(keyCode>=45) && (keyCode<=46) ||
			(keyCode>=16) && (keyCode<=20) ||
			(keyCode>=91) && (keyCode<=93) ||
			(keyCode==13) || (keyCode==9) ||
			(keyCode==8) || (keyCode==27) ||
			(keyCode==144) || (keyCode==12) ||
			(keyCode==224));		
	}

	this.hookKM = function(){
		
		if(TVNC.rcParams.interactive){		
			if(TVNC.iphone){
				console.log("here");
				document.addEventListener("touchstart", TVNC.onTouchStart, false);
				document.addEventListener("touchmove", TVNC.onTouchMove, false);
				document.addEventListener("touchend", TVNC.onTouchEnd, false);			
			}else{
				/* Initialization code. */
				if (window.addEventListener) window.addEventListener('DOMMouseScroll',  TVNC.wheel, false);			
				window.onmousewheel = document.onmousewheel = TVNC.wheel;
				this.vncDivElement.mousedown(TVNC.onTouchStart);
				this.vncDivElement.mouseup(TVNC.onTouchEnd);
				this.vncDivElement.mousemove(TVNC.onTouchMove);
			}
			
/*			this.vncDivElement.mousedown(function(e){
				TVNC.sendMouse(TVNC.mouseX, TVNC.mouseY, e.button, "down");
				var top = TVNC.vncdiv.offsetTop * TVNC.scale;			
				e.stopPropagation();
				e.preventDefault();
			});
			
			this.vncDivElement.mouseup(function(e){
				TVNC.sendMouse(TVNC.mouseX, TVNC.mouseY, e.button, "up");
				e.stopPropagation();
				e.preventDefault();
			});
			
			this.vncDivElement.mousemove(function(e){
				var currentX =   TVNC.serverMouseX(e, false);						
				var currentY = TVNC.serverMouseY(e, false);				
		
				if ((TVNC.mouseX != currentX) || (TVNC.mouseY != currentY)) {				
					TVNC.mouseX = currentX;
					TVNC.mouseY = currentY;
					TVNC.mouseMoved = true;					
					
					TVNC.moveCursorCanvas(e.pageX,e.pageY);
				}
			});
*/
			$(document).keydown(function(e){
				if (TVNC.IsFunctionKey(e.keyCode) ||
					(e.altKey || e.ctrlKey) && (e.altKey != e.ctrlKey)) {						
					TVNC.sendKey(e.keyCode, 0, "down");
					e.stopPropagation();
					e.preventDefault();
				}
				TVNC.lastKeyCode = e.keyCode;
			});
			
			$(document).keypress(function(e){
				var charCode = ($.browser.opera)? e.which : e.charCode;
				if(TVNC.IsFunctionKey(TVNC.lastKeyCode) ||
				   (e.altKey || e.ctrlKey) && (e.altKey != e.ctrlKey)){
					e.stopPropagation();
					e.preventDefault();		
					return;
				}

				TVNC.sendKey(TVNC.lastKeyCode, charCode, "down");
				//alert('Keycode: ' + this.lastKeyCode + ' Charcode: ' + charCode + ' Context: keypress');			
				e.stopPropagation();
				e.preventDefault();		
				
			});

			$(document).keyup(function(e){
				TVNC.lastKeyCode = 0;
				TVNC.sendKey(e.keyCode,0, "up");
				if ($.browser.mozilla && e.altKey) {
					TVNC.sendKey(18, 0, "up");
				}
				e.stopPropagation();
				e.preventDefault();
			});
		}
		this.vncDivElement.bind("contextmenu", function(e){
			return false;
		});
	}
	this.onTouchStart = function(e){		
		if(TVNC.iphone){	
			if(e.touches.length == 1){				
				var button = 0;
				TVNC.mouseX = TVNC.serverMouseX(e, false);						
				TVNC.mouseY = TVNC.serverMouseY(e, false);	
				TVNC.mouseMoved = true;
				TVNC.moveCursorCanvas(e.touches[0].pageX,e.touches[0].pageY);
				TVNC.sendMouse(TVNC.mouseX, TVNC.mouseY, button, "down");											
			}else{
				var button = 2;
				TVNC.sendMouse(TVNC.mouseX, TVNC.mouseY, button, "down");
				TVNC.sendMouse(TVNC.mouseX, TVNC.mouseY, button, "up");					
			}
		}else{
			var button =  e.button;
			TVNC.sendMouse(TVNC.mouseX, TVNC.mouseY, button, "down");
		}

						
		
		e.stopPropagation();
		e.preventDefault();
	}
	this.onTouchMove = function(e){		
		var currentX =   TVNC.serverMouseX(e, false);						
		var currentY = TVNC.serverMouseY(e, false);				

		if ((TVNC.mouseX != currentX) || (TVNC.mouseY != currentY)) {				
			TVNC.mouseX = currentX;
			TVNC.mouseY = currentY;
			TVNC.mouseMoved = true;					
			
			if(!TVNC.iphone){
				TVNC.moveCursorCanvas(e.pageX,e.pageY);
			}else{
				TVNC.moveCursorCanvas(e.touches[0].pageX,e.touches[0].pageY);
			}
		}			
	}
	this.onTouchEnd = function(e){
		var button = (TVNC.iphone)? 0 : e.button;
		TVNC.sendMouse(TVNC.mouseX, TVNC.mouseY, button, "up");
		e.stopPropagation();
		e.preventDefault();		
	
	}
	
	this.connectWebSocket = function() {
		if(TVNC.connected){
			// Create new websocket connection
			var url = "://"+window.location.host;
			if (window.location.protocol.toLowerCase()=="https:") url = "wss"+url;
			else url = "ws"+url;
						
			try{
				
				TVNC.ws = new WebSocket(url);
	
				// Called after connection is established
				TVNC.ws.onopen = function() {									
					TVNC.alive = true;
					TVNC.useAjax = false;					
					TVNC.start();						
				};
	
				// Called when a new message is received
				TVNC.ws.onmessage = function (msg) {					
					if(!TVNC.connected) return;
					if (msg.data=="") return;
					var obj = eval('(' + msg.data + ')');					
					
					if (obj.id != null && obj.id != undefined ) {
						TVNC.serverCmdResult(obj);
					} else{						
						if (obj.windows != null) {						
							TVNC.receiveScreen(obj);
						}
					}
				};
	
				// Called when connection fail
				TVNC.ws.onerror = function(e){
					if(TVNC.alive && !TVNC.useAjax){	
						TVNC.reconnect();
					} else TVNC.start();
					
				}
				
				// Called when connection is closed
				TVNC.ws.onclose = function() { 
					if(TVNC.alive && !TVNC.useAjax){					
						TVNC.reconnect();
					} else TVNC.start();
				};
			}catch(e){
				TVNC.start(); 	//ajax transfer			
			}					
		}
	}
	this.getNextHighestZindex = function(obj){  
	   var highestIndex = 0;  
	   var currentIndex = 0;  
	   var elArray = Array();  
	   if(obj){ elArray = obj.getElementsByTagName('*'); }else{ elArray = document.getElementsByTagName('*'); }  
	   for(var i=0; i < elArray.length; i++){  
		  if (elArray[i].currentStyle){  
			 currentIndex = parseFloat(elArray[i].currentStyle['zIndex']);  
		  }else if(window.getComputedStyle){  
			 currentIndex = parseFloat(document.defaultView.getComputedStyle(elArray[i],null).getPropertyValue('z-index'));  
		  }  
		  if(!isNaN(currentIndex) && currentIndex > highestIndex){ highestIndex = currentIndex; }  
	   }  
	   return(highestIndex+1);  
	}
	  	
	this.reconnect = function(){		
		clearTimeout(TVNC.jsonTimeout);

		TVNC.reconnectireconnectng = true;
		TVNC.connected = false;		
		if(document.getElementById(TVNC.reconnectDivId) == null){
			TVNC.vncdiv.style.cursor = 'default';
			$('#'+TVNC.vncdivId).append('<div id="'+ TVNC.reconnectDivId +'" style="z-index:'+TVNC.getNextHighestZindex(document.body)+';width:100%;height:100%;top:0; left:0; padding:10px; position:absolute; background-color:#000;opacity: .50;filter: alpha(opacity=50);-khtml-opacity: .50;-moz-opacity: .50; -ms-filter: \"alpha(opacity=50)\""></div><div style="-webkit-box-shadow: 1px 1px 15px #000;-moz-box-shadow: 1px 1px 15px #000; position:absolute; top:50%; left:50%; margin-top:-35px; margin-left: -175px; background:#111111;z-index:'+TVNC.getNextHighestZindex(document.body)+'; padding:20px;color:#FFF;-moz-border-radius: 7px;border-radius: 7px; font-size:14px; font-weight:normal; width:250px;height:68px; text-align:center">Connection lost. Reconnecting...<br/><button type="button" id="cancelRecnx" style="margin-top:20px;padding:6px">Abort</button></div>');
			
			$(window).trigger("serverReconnect");
			
			$('#cancelRecnx').click(function(){
				$('#'+TVNC.reconnectDivId).remove();
				TVNC.disconnect();
			});
			$(document).unbind();
			$('#'+TVNC.vncdivId).unbind();

			if (TVNC.useAjax) {
				$.ajaxq(TVNC.queueRequestName);
			}
		}
		TVNC.connect();
		
	}	
	
	this.init = function(dd){	
		for (var o in dd) TVNC.rcParams[o] = dd[o];		
		TVNC.vncdivId = (TVNC.rcParams.divId)? TVNC.rcParams.divId : TVNC.vncdivId;	
		
		var agent = navigator.userAgent.toLowerCase();
		TVNC.iphone = ((agent.indexOf('iphone') != -1) || (agent.indexOf('ipod') != -1) || (agent.indexOf('ipad') != -1));		
		TVNC.vncdiv = document.getElementById(TVNC.vncdivId);
		
		if(!TVNC.vncdiv) throw new Error("the "+ TVNC.vncdivId + " is not available");
			
		TVNC.vncDivElement = $('#'+TVNC.vncdivId);
		TVNC.vncdiv.style.position = 'relative';
		TVNC.vncdiv.style.overflow = 'hidden';
		
		TVNC.supportsCanvas = !!document.createElement('canvas').getContext;

		var path =(TVNC.rcParams.url)?  TVNC.rcParams.url :  window.location.pathname;
		var pathArray = path.split('/');
		TVNC.baseUrl = '';
		for (i = 0; i < pathArray.length - 1; i++) {
			TVNC.baseUrl += pathArray[i];
			TVNC.baseUrl += "/";
		}

		$(window).resize(function(){
			TVNC.zoomDesktop();
		});	

		if($.browser.msie || TVNC.iphone){ 
			TVNC.rcParams.scaled = false;
		}		
		
		TVNC.connect();
	};
}
