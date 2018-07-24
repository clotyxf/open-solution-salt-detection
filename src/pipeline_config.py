import os

from deepsense import neptune
from attrdict import AttrDict

from .utils import read_params

ctx = neptune.Context()
params = read_params(ctx)

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
SEED = 1234

SIZE_COLUMNS = ['height', 'width']
X_COLUMNS = ['file_path_image']
Y_COLUMNS = ['file_path_mask']
DEPTH_COLUMN = ['z']
CHANNELS_SIGMOID = ['salt']

GLOBAL_CONFIG = {'exp_root': params.experiment_dir,
                 'num_workers': params.num_workers,
                 'num_classes': 2,
                 'img_H-W': (params.image_h, params.image_w),
                 'batch_size_train': params.batch_size_train,
                 'batch_size_inference': params.batch_size_inference,
                 'loader_mode': params.loader_mode,
                 }

TRAINING_CONFIG = {'epochs': params.epochs_nr,
                   'shuffle': True,
                   'batch_size': params.batch_size_train,
                   }

SOLUTION_CONFIG = AttrDict({
    'env': {'cache_dirpath': params.experiment_dir},
    'execution': GLOBAL_CONFIG,
    'xy_splitter': {
        'unet': {'x_columns': X_COLUMNS,
                 'y_columns': Y_COLUMNS,
                 },
    },
    'reader': {
        'unet': {'x_columns': X_COLUMNS,
                 'y_columns': Y_COLUMNS,
                 },
    },
    'loader': {'dataset_params': {'h': params.image_h,
                                  'w': params.image_w,
                                  'pad_method': params.pad_method,
                                  'image_source': params.image_source,
                                  'divisor': 64,
                                  'target_format': params.target_format
                                  },
               'loader_params': {'training': {'batch_size': params.batch_size_train,
                                              'shuffle': True,
                                              'num_workers': params.num_workers,
                                              'pin_memory': params.pin_memory
                                              },
                                 'inference': {'batch_size': params.batch_size_inference,
                                               'shuffle': False,
                                               'num_workers': params.num_workers,
                                               'pin_memory': params.pin_memory
                                               },
                                 },
               },
    'model': {
        'unet': {
            'architecture_config': {'model_params': {'n_filters': params.n_filters,
                                                     'conv_kernel': params.conv_kernel,
                                                     'pool_kernel': params.pool_kernel,
                                                     'pool_stride': params.pool_stride,
                                                     'repeat_blocks': params.repeat_blocks,
                                                     'batch_norm': params.use_batch_norm,
                                                     'dropout': params.dropout_conv,
                                                     'in_channels': params.image_channels,
                                                     'out_channels': params.unet_output_channels,
                                                     'nr_outputs': params.nr_unet_outputs,
                                                     'encoder': params.encoder,
                                                     'activation': params.unet_activation
                                                     },
                                    'optimizer_params': {'lr': params.lr,
                                                         },
                                    'regularizer_params': {'regularize': True,
                                                           'weight_decay_conv2d': params.l2_reg_conv,
                                                           },
                                    'weights_init': {'function': 'xavier',
                                                     },
                                    },
            'training_config': TRAINING_CONFIG,
            'callbacks_config': {'model_checkpoint': {
                'filepath': os.path.join(GLOBAL_CONFIG['exp_root'], 'checkpoints', 'unet', 'best.torch'),
                'epoch_every': 1,
                'metric_name': params.validation_metric_name,
                'minimize': params.minimize_validation_metric},
                'lr_scheduler': {'gamma': params.gamma,
                                 'epoch_every': 1},
                'training_monitor': {'batch_every': 0,
                                     'epoch_every': 1},
                'experiment_timing': {'batch_every': 0,
                                      'epoch_every': 1},
                'validation_monitor': {'epoch_every': 1,
                                       'data_dir': params.train_images_dir,
                                       'loader_mode': params.loader_mode},
                'neptune_monitor': {'model_name': 'unet',
                                    'image_nr': 4,
                                    'image_resize': 0.2},
                'early_stopping': {'patience': params.patience,
                                   'metric_name': params.validation_metric_name,
                                   'minimize': params.minimize_validation_metric},
            }
        },
    },
    'tta_generator': {'flip_ud': True,
                      'flip_lr': True,
                      'rotation': True,
                      'color_shift_runs': False},
    'tta_aggregator': {'method': params.tta_aggregation_method,
                       'nthreads': params.num_threads
                       },
    'thresholder': {'threshold_masks': params.threshold_masks,
                    'threshold_seeds': params.threshold_seeds,
                    'threshold_borders': params.threshold_borders,
                    },
    'watershed': {},
    'dropper': {'min_mask_size': params.min_mask_size,
                'min_seed_size': params.min_seed_size
                },
    'postprocessor': {'channels': {'sigmoid': CHANNELS_SIGMOID
                                   }
                      }
})