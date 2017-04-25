import os
import numpy as np
import tensorflow as tf
import data_helpers

class CNN_Sentence(object):

    def __init__(self,
                batch_size = 256,
                checkpoint_dir = './runs/1492510012/checkpoints/',
                allow_soft_placement = True,
                log_device_placement = False
                ):
        self.batch_size = 256

        print checkpoint_dir
        checkpoint_file = tf.train.latest_checkpoint(checkpoint_dir)
        graph = tf.Graph()
        with graph.as_default():
            session_conf = tf.ConfigProto(
                    allow_soft_placement = allow_soft_placement,
                    log_device_placement = log_device_placement)
            self.sess = tf.Session(config=session_conf)
            with self.sess.as_default():
                self.saver = tf.train.import_meta_graph('{}.meta'.format(checkpoint_file))
                self.saver.restore(self.sess, checkpoint_file)
                self.input_x = graph.get_operation_by_name('input_x').outputs[0]
                self.dropout_keep_prob = graph.get_operation_by_name('dropout_keep_prob').outputs[0]
                self.predictions = graph.get_operation_by_name('output/predictions').outputs[0]

    def predict(self, x_raw, print_info = False):
        with self.sess.as_default():
            x_test, vocab_vector = data_helpers.build_vocabulary(x_raw)
            batches = data_helpers.batch_iter(list(x_test), self.batch_size, 1, shuffle=False)
            
            if print_info:
                count = 0
                total = int((len(x_test)-1) / self.batch_size) + 1
                print 'Batch Size: ', self.batch_size
                print 'Num Batches: ', total

            all_predictions = []
            
            for x_test_batch in batches:
                if print_info:
                    count += 1
                    if count % 100 == 1:
                        print count, ' / ', total
                batch_predictions = self.sess.run(self.predictions, {self.input_x: x_test_batch, self.dropout_keep_prob: 1.0})
                all_predictions = np.concatenate([all_predictions, batch_predictions])
            return all_predictions
        
    def evaluate(self, y_test, all_predictions):
        correct_predictions = float(sum(all_predictions == y_test))
        accuracy = correct_predictions/float(len(y_test))
        print("Total number of test examples: {}".format(len(y_test)))
       
        print ''
        print 'Confusion Matrix:'
        matrix = np.zeros([2,2])
        for idx, predict in enumerate(all_predictions):
            matrix[1-int(y_test[idx])][1-int(predict)] += 1
        print 'Truth / Predicted       Positive DM      Negative DM'
        print 'Positive DM:              {}             {}'.format(str(matrix[0,0]), str(matrix[0,1]))
        print 'Negative DM:              {}             {}'.format(str(matrix[1,0]), str(matrix[1,1]))
        print ''

        recall = matrix[1,1] / (matrix[1,1] + matrix[1,0])
        precision = matrix[1,1] / (matrix[1,1] + matrix[0,1])
        print("Accuracy :    {:g}".format(accuracy))
        print("Recall   :    {:g}".format(recall))
        print("Precision:    {:g}".format(precision))
        return accuracy


if __name__ == '__main__':
    posfile = 'data/positive.test'
    negfile = 'data/negative.test'
    x_raw, y_test = data_helpers.load_data_and_labels(posfile, negfile)
    y_test = np.argmax(y_test, axis=1)
    cnn_sentence = CNN_Sentence()
    predictions = cnn_sentence.predict(x_raw, print_info = False)
    #print predictions
    #print y_test
    accuracy = cnn_sentence.evaluate(y_test, predictions)
