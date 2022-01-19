document.addEventListener('DOMContentLoaded', () => {
    // Activates the page buttons
    comment();
    run_like();
    edit_save();
});

function comment() {
    // Hide all the comments
    document.querySelectorAll('.comments').forEach(comment => {
        comment.style.display = 'none';
    })
    // Show comment
    document.querySelectorAll(`.button-showComments`).forEach(button => {
        button.onclick = function () {
            document.querySelector(`#comment-on-${button.dataset.showcommentsid}`).style.display = 'block';
        }
    })
    // Submit comment
    document.querySelectorAll('.submit-comment').forEach(input => {
        input.onclick = make_comment;
    })
}

function make_comment() {
    // send comment to server
    var post_id = this.dataset.input;
    var comment = document.querySelector(`#make-comment-${post_id}`).value;
    fetch(`/comment/${post_id}`, {
        method: "POST",
        body: JSON.stringify({
            comment: `${comment}`
        })
    })
    .then(response => response.json())
    .then(response => {
        // Add the new comment to the comment field
        var div = document.createElement('div');
        var name = document.createElement('p');
        var comment = document.createElement('p');
        var timestamp = document.createElement('p');
        var a = document.createElement('a');

        a.setAttribute('href', `profile/${response.name}`);
        a.innerHTML = response.name
        name.className = 'username';
        name.append(a);

        comment.innerHTML = response.comment;
        timestamp.innerHTML = moment(response.timestamp).format('MMM D YYYY, h:mm A');
        timestamp.className = 'timestamp';

        div.className = "all-comments";
        div.append(name);
        div.append(comment);
        div.append(timestamp);

        var c = document.querySelector(`#comment-on-${post_id}`).append(div);
        document.querySelector(`#make-comment-${post_id}`).value = '';
    })
}

function run_like() {
    // Select all like buttons
    document.querySelectorAll('.button-like').forEach(button => {
        button.onclick = like;
    });
}

function like() {
    // Send the post id to the server
    fetch(`/like/${this.dataset.id}`)
    .then(response => response.json())
    .then(response => {
        document.querySelector(`#like-${this.dataset.id}`).innerHTML = response.count;
        if (response.liked){
            document.querySelector(`#button-${this.dataset.id}`).innerHTML = "Like";
        } else {
            document.querySelector(`#button-${this.dataset.id}`).innerHTML = "Unlike";
        }
        // Run the function again
        run_like();
    })
}

function edit_save() {
    // Select all Edit buttons
    document.querySelectorAll("a").forEach(a => {
        if (a.innerHTML == 'Edit'){
            a.onclick = edit;
        } else {
            a.onclick = save;
        }
    });
}

function edit() {
    // fill in the new textarea with the content of the post gotten from the server
    fetch(`/edit_post/${this.dataset.id}`)
    .then(response => response.json())
    .then(response => {
        var textarea = document.createElement('textarea');
        textarea.innerHTML = response.post;
        textarea.className = 'form-control';
        textarea.id = `textarea-${this.dataset.id}`;
        textarea.style.height = '160px';
        document.querySelector(`#post-${this.dataset.id}`).innerHTML = '';
        document.querySelector(`#post-${this.dataset.id}`).append(textarea);
        document.querySelector(`#edit-${this.dataset.id}`).innerHTML = 'Save';
        edit_save();
    });
}

function save() {
    // Save the new content of the post
    const new_text = document.querySelector(`#textarea-${this.dataset.id}`).value;
    fetch(`/edit_post/${this.dataset.id}`, {
        method: 'POST',
        body: JSON.stringify({
            text: `${new_text}`
        })
    })
    .then(response => response.json())
    .then(response => {
        const p = document.createElement('p');
        p.innerHTML = response.new_post;
        document.querySelector(`#post-${this.dataset.id}`).innerHTML = '';
        document.querySelector(`#post-${this.dataset.id}`).append(p);
        document.querySelector(`#edit-${this.dataset.id}`).innerHTML = 'Edit';
        edit_save();
    })
}
