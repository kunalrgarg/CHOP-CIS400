import React, { Component } from 'react';
import ReactDOM from 'react-dom';

export default class DynamicResults extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {

        }
    }


    // renderResults = () => {
    //     let model = this.props.model;

    //     let resultsUI = model.map((m) => {
    //         let key = m.key;
    //         let type = m.type || "text";
    //         let props = m.props || {};

    //         return (
    //             <div key={key}>
    //                 <input {...props}
    //                     ref={(key)=>{this[m.key] = key}}
    //                     type={type}
    //                     key={i + m.key}
    //                     // onChange={(e=>{this.onChange(e, key)})}

    //                 />
    //             </div>
    //         );

    //     });

    //     return resultsUI;
    // }


    // render() {
    //     let title = this.props.title || "Dynamic Results";

    //     return (
    //         <div>
    //             <h3>{title}</h3>
    //             {this.renderResults()}
    //         </div>
    //     )
    // }
    
}