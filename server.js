const express = require('express');
const axios = require('axios');
const bitcore = require('bitcore-lib');

const app = express();
app.use(express.json());


async function getFeeRate() {
    try {
        const response = await axios.get('https://api.blockcypher.com/v1/btc/test3');
        const feeRate = response.data.high_fee_per_kb; // high_fee_per_kb for fastest confirmation
        return feeRate / 1000; // Convert from satoshis per KB to satoshis per byte
    } catch (error) {
        console.error('Error fetching fee rate:', error.message);
        return 20; // Default to a safe fee rate (20 satoshis per byte)
    }
}

async function handleTransaction_return(amount, address) {
    try {
        const privateKeyWIF = 'your-private-key-in-WIF-format';
        const sourceAddress = 'your-source-address';
        
        if (!isValidAddress(address)) {
            throw new Error('Invalid recipient address');
        }
        
        const utxosResponse = await axios.get(`https://api.blockcypher.com/v1/btc/test3/addrs/${sourceAddress}?unspentOnly=true`);
        const utxos = utxosResponse.data.txrefs || [];
        
        const feeRate = await getFeeRate();
        
        // Create a transaction
        const transaction = new bitcore.Transaction()
            .from(utxos)
            .to(address, amount)
            .change(sourceAddress)
            .feePerByte(feeRate) // Use fee rate per byte
            .sign(bitcore.PrivateKey.fromWIF(privateKeyWIF));
        
        const serializedTx = transaction.serialize();
        const txId = transaction.hash;
        
        const broadcastResponse = await axios.post('https://api.blockcypher.com/v1/btc/test3/txs/push', { tx: serializedTx });
        console.log('Transaction broadcasted successfully:', txId);
        
        await waitForConfirmations(txId, 2);
    } catch (error) {
        console.error('Error handling transaction:', error.message);
    }
}

function isValidAddress(address) {
    try {
        new bitcore.Address(address);
        return true;
    } catch (e) {
        return false;
    }
}

async function waitForConfirmations(txId, minConfirmations) {
    return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
            try {
                const response = await axios.get(`https://api.blockcypher.com/v1/btc/test3/txs/${txId}`);
                const confirmations = response.data.confirmations || 0;
                
                console.log(`Transaction ${txId} has ${confirmations} confirmations`);
                
                if (confirmations >= minConfirmations) {
                    clearInterval(interval);
                    console.log(`Transaction ${txId} has been confirmed.`);
                    resolve();
                }
            } catch (error) {
                console.error('Error checking confirmations:', error.message);
            }
        }, 60000);
    });
}

async function getAmountSentBetweenAddresses(senderAddress, recipientAddress) {
    try {
        // Fetch transaction history for the sender address
        
        const transactionsResponse = await axios.get(`https://api.blockcypher.com/v1/btc/main/addrs/${senderAddress}/full`);
        const transactions = transactionsResponse.data.txs || [];
        
        let totalSent = 0;
        
        // Iterate over all transactions to find those involving the recipient address
        for (const tx of transactions) {
            for (const output of tx.outputs) {
                if (output.addresses && output.addresses.includes(recipientAddress)) {
                    // Check if the transaction was made in the last 5 minutes
                    const txTime = new Date(tx.received).getTime(); // Transaction time in milliseconds
                    const currentTime = Date.now(); // Current time in milliseconds
                    const timeDifference = (currentTime - txTime) / 1000 / 60; // Difference in minutes
                    console.log(33);
                    if (timeDifference <= 5) {
                        // Sum the amounts sent to the recipient address if it was in the last 5 minutes
                        totalSent = output.value; // value is in satoshis
                        console.log(44);
                        // Convert the amount to BTC
                        const totalSentBTC = totalSent / 1e8; // Convert from satoshis to BTC
                        return totalSentBTC;
                    } else {
                        return "Not 5 min";
                    }
                }
            }
        }

    } catch (error) {
        console.error('Error fetching or processing transactions:', error.message);
        throw error;
    }
}

// API Endpoint for handling transactions
app.post('/transaction', async (req, res) => {
    const { amount, address } = req.body;
    try {
        const result = await handleTransaction_return(amount, address);
        res.json(result);
    } catch (error) {
        res.status(500).json({ status: 'error', message: error.message });
    }
});


app.get('/check-amount', async (req, res) => {
    const { senderAddress, recipientAddress } = req.query;

    // Check if addresses are provided
    if (!senderAddress || !recipientAddress) {
        return res.status(400).send('Sender and recipient addresses are required.');
    }

    try {
        // Validate the sender's address
        const isValid_sender = await isValidAddress(senderAddress);
        const isValid_recipient = await isValidAddress(recipientAddress);

        if (!isValid_sender || !isValid_recipient) {
            return res.status(400).send('Invalid sender address.');
        }

        // Proceed with your logic here...
    } catch (error) {
        console.error('Error validating address:', error.message);
        return res.status(500).send('Error validating the sender address.');
    }

    console.log(222);

    try {
        const intervalTime = 60000; // 60 seconds
        const maxDuration = 5 * 60 * 1000; // 1 hour in milliseconds
 
        // Set up an interval to run every minute
        const intervalId = setInterval(async () => {
            try {
                const amountSent = await getAmountSentBetweenAddresses(senderAddress, recipientAddress);
                console.log(`Amount sent: ${amountSent} BTC`);
                // You can choose to store or process the amountSent as needed
            } catch (error) {
                console.error('Error fetching amount:', error.message);
            }
        }, intervalTime);
        
        // Stop the interval after 1 hour
        setTimeout(() => {
            clearInterval(intervalId);
            console.log('Stopped checking after 1 hour.');
        }, maxDuration);
        
        // Immediate response for the GET request
        res.json({ senderAddress, recipientAddress, amountSent });
    } catch (error) {
        res.status(500).send('Error processing your request.');
    }
});

app.get('/check-wallet', async (req, res) => {
    const { senderAddress, recipientAddress } = req.query;

    // Check if addresses are provided
    if (!senderAddress || !recipientAddress) {
        return res.status(400).send('Sender and recipient addresses are required.');
    }

    try {
        // Validate the sender's address
        const isValid_sender = await isValidAddress(senderAddress);
        const isValid_recipient = await isValidAddress(recipientAddress);
        
        if (!isValid_sender || !isValid_recipient) {
            return res.status(400).send('Invalid sender address.');
        }
        return res.status(200).send('Valid sender address.');
        // Proceed with your logic here...
    } catch (error) {
        console.error('Error validating address:', error.message);
        return res.status(500).send('Error validating the sender address.');
    }
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

