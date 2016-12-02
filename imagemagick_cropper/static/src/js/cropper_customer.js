function magick_crop(){
    openerp.jsonRpc("/magick_crop", "call", {
        'image_url': $("#image").attr('src'),
        'dataX': $("#dataX").val(),
        'dataY': $("#dataY").val(),
        'dataWidth': $("#dataWidth").val(),
        'dataHeight': $("#dataHeight").val(),
        'dataRotate': $("#dataRotate").val(),
        'dataScaleX': $("#dataScaleX").val(),
        'dataScaleY': $("#dataScaleY").val(),
    }).done(function(data){
        if(data === 'Magic Crop Completed!')
            location.reload();
    });
}


