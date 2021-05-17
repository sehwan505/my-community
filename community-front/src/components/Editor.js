import React, {useState} from "react";
import "@toast-ui/editor/dist/toastui-editor.css";
import { Editor } from "@toast-ui/react-editor";
import axios from "axios";
import CSRFToken from "../components/csrftoken.js";
import {useHistory} from "react-router-dom";

const DraftEditor = ({user}) => {
  const editorRef = React.createRef();
  const [content, setContent] = useState({});
  const [postTitle , setPostTitle] = useState("");
  const [section , setSection] = useState("1");
  const history = useHistory();

  const handleClick = (event) => {
	event.preventDefault();
    setContent({
      content: editorRef.current.getInstance().getMarkdown(),
    });
	console.log(content);
  };

  const onSubmit = async (event) => {
    event.preventDefault();
	setContent({
		content: editorRef.current.getInstance().getMarkdown(),
	});
	console.log(section);
	var csrftoken = CSRFToken();
	const config = {
		headers: {
			'Authorization' : `JWT ${localStorage.getItem('token')}`	
		}
	}
    await axios.post('http://127.0.0.1:8000/api/post/add/', {
        title: postTitle,
        content: content.content,
        writer_id: user.user_pk,
        writer_name: user.username,
		section : section,
		csrfmiddlewaretoken	: csrftoken
    }, config).then((response) => {
	  history.push('/');
    })
    .catch((error) => {
    // 예외 처리
	  console.log(error);
	})
  }

  const onChangeTitle = (event) => {
    const {
      target: { value },
    } = event;
    setPostTitle(value);
  }

  const onChangeSection = (event) => {
    const {
      target: { value },
    } = event;
    setSection(value);
	console.log(value);
  }

  const uploadImage = (blob) => {
	let formData = new FormData();

	console.log(blob);
    // file in a 'multipart/form-data' request
    formData.append('image', blob.data);
	let csrftoken = CSRFToken();
    return fetch('http://127.0.0.1:8000/api/post/upload_image/', {
        method: 'POST',
		headers: {
			'Content-type' : 'multipart/form-data' ,
			'Authorization' : `JWT ${localStorage.getItem('token')}`
		},
        body: {
			data: formData,
			csrfmiddlewaretoken	: csrftoken
		}
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Server or network error');
    });
  }

  const onAddImageBlob = (blob, callback) => {
    uploadImage(blob)
        .then(response => {
			console.log(response);
            if (!response.success) {
                throw new Error('Validation error');
            }
            callback(response.data.url, 'alt text');
        }).catch(error => {
            console.log(error);
        });
};

  return (
    <>
	<form onSubmit={onSubmit}>
	  <input
        value={postTitle}
        placeholder="제목"
        type="text"
        onChange={onChangeTitle}
      />
	  <select name="section" onChange={onChangeSection} value={section} >
			<option value="1">정치</option>
			<option value="2">게임</option>
			<option value="3">연예</option>
			<option value="4">유머</option>
	  </select>
      <Editor
        previewStyle="vertical"
        height="300px"
        initialEditType="wysiwyg"
        placeholder="글쓰기"
        ref={editorRef}
		hooks={{
			addImageBlobHook: onAddImageBlob
		}}
      />
      <button onClick={handleClick}>저장</button>
	  <input type="submit" value="에딧"/>
	  </form>
    </>
  );
};
export default DraftEditor;