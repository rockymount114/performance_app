var name;

    new Autocomplete('#autocomplte', {
        search: input => {
            const url = '/search/?name=${input}';
            return new Promise(resolve =>{
                fetch(url).then(response => response.json()).then(data =>{
                    resolve(data.name)
                })
            })
        },

        onsubmit: result => {
            name = result;
        }
    })

    $('#ull').click(function (e){
        $.ajax({
            url: '',
            type: 'GET',
            data: {
                valname: name,
            },
            success: function (response){
                window.location = response.urlLink;
            }
        })
    })