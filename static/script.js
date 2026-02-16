function popup(value, form)
{
    let popup = document.getElementById('pop');
    popup.innerHTML = value;
    popup.style.visibility = 'visible';
    popup.style.width = '150px'
    popup.style.height = '50px'
    popup.style.backgroundColor ='#780000';
    popup.style.fontSize = '40px'
    popup.transitionend;
    document.getElementById(form).submit();
}
