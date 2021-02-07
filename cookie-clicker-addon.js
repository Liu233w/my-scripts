function liu233wInit() {
  const timer = setInterval(() => {
    if (Game && Game.playCookieClickSound) {
      console.log('Disabling cookie clicking sound')
      Game.playCookieClickSound = ()=>{return}

      // cleanup
      clearInterval(timer)
    } else {
      console.log('waiting game loaded')
    }
  }, 500)
}

liu233wInit()