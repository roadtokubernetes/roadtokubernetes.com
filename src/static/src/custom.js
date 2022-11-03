
 var themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
 var themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

 // Change the icons inside the button based on previous settings
 if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
     themeToggleLightIcon.classList.remove('hidden');
 } else {
     themeToggleDarkIcon.classList.remove('hidden');
 }

 var themeToggleBtn = document.getElementById('theme-toggle');

 themeToggleBtn.addEventListener('click', function() {

     // toggle icons inside button
     themeToggleDarkIcon.classList.toggle('hidden');
     themeToggleLightIcon.classList.toggle('hidden');

     // if set via local storage previously
     if (localStorage.getItem('color-theme')) {
         if (localStorage.getItem('color-theme') === 'light') {
             document.documentElement.classList.add('dark');
             localStorage.setItem('color-theme', 'dark');
         } else {
             document.documentElement.classList.remove('dark');
             localStorage.setItem('color-theme', 'light');
         }

     // if NOT set via local storage previously
     } else {
         if (document.documentElement.classList.contains('dark')) {
             document.documentElement.classList.remove('dark');
             localStorage.setItem('color-theme', 'light');
         } else {
             document.documentElement.classList.add('dark');
             localStorage.setItem('color-theme', 'dark');
         }
     }
     
});



const classMap = {
    h1: 'text-4xl  my-2',
    h2: 'text-3xl my-2',
    h3: 'text-2xl  my-2',
    h4: 'text-xl  my-2',
    h5: 'text-lg my-2',
    code: 'dark:text-rose-400 text-rose-600 text-left',
    'pre code': 'dark:text-white text-white bg-black text-left',
    }

    const bindings = Object.keys(classMap)
    .map(key => ({
        type: 'output',
        regex: new RegExp(`<${key}(.*)>`, 'g'),
        replace: `<${key} class="${classMap[key]}" $1>`
    }));

    const preCode = {
        type: 'output',
        regex: new RegExp(`<pre>\\s*<code (.*)>`, 'g'),
        replace: `<pre><code class="${classMap['pre code']}" $1>`
    }

function inputToSafeMarkdown (textInput) {
    const extensions = [...bindings, preCode,]
    var converter = new showdown.Converter({"extensions":extensions })
    // converter.addExtension(customClassExt);
    let markdown = textInput
    let markedContent = converter.makeHtml(markdown);
    let sanitizedContent = DOMPurify.sanitize(markedContent)
    return DOMPurify.sanitize(sanitizedContent)
}

function performMarkdown(){ 
    const markdownElements = document.getElementsByClassName('markdown')
    for (let el of markdownElements) {
        el.innerHTML = inputToSafeMarkdown(el.innerHTML)
        el.classList.remove('hidden')
        el.classList.remove('markdown')
    }
    if (hljs) {
        hljs.highlightAll();
    }
}
performMarkdown()

function dynamicInputElementButtonRemoval(){
    const inputElementRemoveButton = document.getElementsByClassName("input-element-container-remove-button")
    for (let el of inputElementRemoveButton) {
        el.removeEventListener("click", null)
        el.addEventListener("click", (e)=>{
            e.preventDefault()
            const dataset = el.dataset
        
            const removeConfirm = dataset.removeConfirm ? true : false
            const isReady = dataset.ready ? true : false
            if (!isReady) {
                let parentContainerEl = el.closest(".input-element-container")
                console.log(removeConfirm)
                if (removeConfirm) {
                    if (confirm("Are you sure you want to remove this?") == true){
                        parentContainerEl.remove()
                    }
                } else {
                    parentContainerEl.remove()
                }
                el.dataset['ready'] = true
            }
        })
    }
}
dynamicInputElementButtonRemoval()
document.body.addEventListener('htmx:afterSwap', function(evt) {
    dynamicInputElementButtonRemoval()
    performMarkdown()
});
