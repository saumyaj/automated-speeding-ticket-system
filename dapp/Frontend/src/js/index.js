
import React from 'react'
import ReactDOM from 'react-dom'
import Web3 from 'web3'
import $ from 'jquery'
import './../css/index.css'

const mystyle = {
	color: "white",
    backgroundColor: "dodgerblue",
    padding: "10px",
    fontSize: "20px",
    fontFamily: "Arial",
    borderRadius: "12px",
    marginLeft:"200px",
    marginTop:"40px",
    };

class App extends React.Component {
	constructor(props){
	   super(props)
	   this.state = {
	      input2:"",
	      etherbet:"",
	      showSubmit:false,
	   }
	   if(typeof web3 != 'undefined'){
	      console.log("Using web3 detected from external source like Metamask")
	      // this.web3 = new Web3(web3.currentProvider)
	      this.web3 = new Web3(ethereum);
	      try {
            // Request account access if needed
            	ethereum.enable();
            // Acccounts now exposed
	        } catch (error) {
	            console.log('ethereum enable error')
	        }
	   }else{
	      this.web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"))
	   }
	   const MyContract = web3.eth.contract([
	{
		"constant": false,
		"inputs": [],
		"name": "kill",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "pay",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"payable": true,
		"stateMutability": "payable",
		"type": "fallback"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	}
])
	   this.state.ContractInstance = MyContract.at("0xE2f2164BEE931490B96263a937598e8a3Cf75E5C")
	}




handleChange(event){
	this.setState({input2:event.target.value})
}
handleChange1(event){
	this.setState({etherbet:event.target.value})
}
componentDidMount(){
      this.updateState()
      this.setupListeners()
setInterval(this.updateState.bind(this), 10e3)
   }
updateState(){
      
}
// Listen for events and executes the voteNumber method
   setupListeners(){
      let liNodes = this.refs.numbers.querySelectorAll('li')
      liNodes.forEach(number => {
         number.addEventListener('click', event => {
            event.target.className = 'number-selected'
            this.voteNumber(parseInt(event.target.innerHTML), done => {
// Remove the other number selected
               for(let i = 0; i < liNodes.length; i++){
                  liNodes[i].className = ''
               }
            })
         })
      })
   }
abc(r){
	console.log(r);
}

handleSubmit(){
	let value = this.state.input2;
	let address = 'https://us-central1-cc2020-project2.cloudfunctions.net/function-3'
	let url = address + '?ticketId=' + this.state.input2
	$.ajax({
		url: url,
		success: this.abc
	});
	this.voteNumber(0, done => {
// Remove the other number selected
              
    })
}

voteNumber(number, cb){
      let bet = this.refs['ether-bet'].value
if(!bet) bet = 0.1
if(parseFloat(bet) < this.state.minimumBet){
         alert('You must bet more than the minimum')
         cb()
      } else {
         this.state.ContractInstance.pay({
            gas: 300000,
            from: web3.eth.accounts[0],
            value: web3.toWei(bet, 'ether')
         }, (err, result) => {
            cb()
         })
      }
   }
   
render(){
      return (
         <div className="main-container">
            <h1>Welcome to Speed Ticket Payment Portal</h1>

<hr/>
<h2>Please use your ticket id to pay for your ticket.</h2>
<label>
               <b><label style={{width:"120px",display:"inline-block"}}>Fine Amount:</label> <input className="bet-input" value={this.state.etherbet} onChange={(event)=>this.handleChange1(event)}  ref="ether-bet" type="number" /></b> ether
               <br/><br/><br/><br/>
            </label>
   
            <div>
            	<b><label style={{width:"120px",display:"inline-block"}}>Ticket ID:</label>  <input className="bet-input" type="text" value={this.state.input2} onChange={(event)=>this.handleChange(event)}/></b>
            	</div>
            	<div style={{margin:"10px"}} className={this.state.etherbet.length>0 && this.state.input2.length>0?"":"hide"}>
            	{
            
            	<button style={mystyle} onClick={()=>this.handleSubmit()}>Submit</button>
            }
            </div>
         </div>
      )
   }
}
ReactDOM.render(
   <App />,
   document.querySelector('#root')
)