function myFunction() {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();

    ul = document.getElementById("search_items");
    li = ul.getElementsByTagName("article");
    for (i = 0; i < li.length; i++) {
        c = li[i].getElementsByTagName("div")[0];
        b = c.getElementsByTagName("h2")[0];
        a = b.getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}
